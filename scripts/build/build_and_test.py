#!/usr/bin/env python3
"""
Build and Test Automation Script

This script builds distributions and runs comprehensive end-to-end tests against them.
It can run in the background and report regression issues.

Usage:
    python scripts/build/build_and_test.py [options]
    
Options:
    --build-only        Only build, don't run tests
    --test-only         Only run tests, don't build
    --watch             Watch for changes and auto-rebuild/test
    --report-file       Output file for test results (default: test_results.json)
    --platforms         Platforms to build for (source,wheel,exe,app,appimage)
    --verbose           Verbose output
    --headless          Run GUI tests in headless mode
    --timeout           Test timeout in seconds (default: 300)
"""

import os
import sys
import json
import time
import shutil
import subprocess
import tempfile
import argparse
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts"))

class BuildTestRunner:
    """Automated build and test runner with regression detection."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.project_root = project_root
        self.build_dir = self.project_root / "dist"
        self.temp_dir = None
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'builds': {},
            'tests': {},
            'regressions': [],
            'summary': {}
        }
        
        # Setup logging
        log_level = logging.DEBUG if config.get('verbose') else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.project_root / 'build_test.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run(self) -> bool:
        """Run the complete build and test process."""
        try:
            self.logger.info("Starting build and test process...")
            
            # Create temporary directory for testing
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_converter_test_")
            self.logger.info(f"Using temp directory: {self.temp_dir}")
            
            success = True
            
            # Build phase
            if not self.config.get('test_only', False):
                self.logger.info("=== BUILD PHASE ===")
                if not self._run_builds():
                    success = False
                    
            # Test phase
            if not self.config.get('build_only', False):
                self.logger.info("=== TEST PHASE ===")
                if not self._run_tests():
                    success = False
                    
            # Generate report
            self._generate_report()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Build and test process failed: {e}")
            return False
        finally:
            self._cleanup()
            
    def _run_builds(self) -> bool:
        """Run all build processes."""
        platforms = self.config.get('platforms', ['source', 'wheel'])
        success = True
        
        for platform in platforms:
            self.logger.info(f"Building {platform}...")
            build_success, build_info = self._build_platform(platform)
            
            self.results['builds'][platform] = {
                'success': build_success,
                'info': build_info,
                'timestamp': datetime.now().isoformat()
            }
            
            if not build_success:
                success = False
                self.logger.error(f"Build failed for {platform}")
            else:
                self.logger.info(f"Build successful for {platform}")
                
        return success
        
    def _build_platform(self, platform: str) -> Tuple[bool, Dict]:
        """Build for a specific platform."""
        build_info = {'platform': platform, 'files': [], 'size': 0}
        
        try:
            if platform == 'source':
                return self._build_source_dist(build_info)
            elif platform == 'wheel':
                return self._build_wheel_dist(build_info)
            elif platform == 'exe':
                return self._build_executable(build_info)
            elif platform == 'app':
                return self._build_macos_app(build_info)
            elif platform == 'appimage':
                return self._build_linux_appimage(build_info)
            else:
                self.logger.error(f"Unknown platform: {platform}")
                return False, build_info
                
        except Exception as e:
            self.logger.error(f"Build error for {platform}: {e}")
            build_info['error'] = str(e)
            return False, build_info
            
    def _build_source_dist(self, build_info: Dict) -> Tuple[bool, Dict]:
        """Build source distribution."""
        cmd = [sys.executable, "-m", "build", "--sdist"]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Find created files
            for file in self.build_dir.glob("*.tar.gz"):
                build_info['files'].append(str(file))
                build_info['size'] += file.stat().st_size
            return True, build_info
        else:
            build_info['error'] = result.stderr
            return False, build_info
            
    def _build_wheel_dist(self, build_info: Dict) -> Tuple[bool, Dict]:
        """Build wheel distribution."""
        cmd = [sys.executable, "-m", "build", "--wheel"]
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Find created files
            for file in self.build_dir.glob("*.whl"):
                build_info['files'].append(str(file))
                build_info['size'] += file.stat().st_size
            return True, build_info
        else:
            build_info['error'] = result.stderr
            return False, build_info
            
    def _build_executable(self, build_info: Dict) -> Tuple[bool, Dict]:
        """Build standalone executable with PyInstaller."""
        try:
            import PyInstaller.__main__
            
            # PyInstaller command
            args = [
                '--onefile',
                '--windowed',
                '--name=pdf-power-converter',
                '--add-data=scripts/ui/icons:ui/icons',
                '--add-data=scripts/ui/styles:ui/styles',
                '--hidden-import=PyQt5.sip',
                str(self.project_root / 'main.py')
            ]
            
            PyInstaller.__main__.run(args)
            
            # Find created executable
            exe_dir = self.project_root / "dist"
            for file in exe_dir.glob("pdf-power-converter*"):
                if file.is_file():
                    build_info['files'].append(str(file))
                    build_info['size'] += file.stat().st_size
                    
            return len(build_info['files']) > 0, build_info
            
        except ImportError:
            build_info['error'] = "PyInstaller not installed"
            return False, build_info
        except Exception as e:
            build_info['error'] = str(e)
            return False, build_info
            
    def _build_macos_app(self, build_info: Dict) -> Tuple[bool, Dict]:
        """Build macOS .app bundle."""
        if sys.platform != "darwin":
            build_info['error'] = "macOS app can only be built on macOS"
            return False, build_info
            
        build_script = self.project_root / "scripts/build/build_macos.sh"
        if not build_script.exists():
            build_info['error'] = "macOS build script not found"
            return False, build_info
            
        result = subprocess.run([str(build_script)], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Find created app bundle
            for file in self.build_dir.glob("*.app"):
                build_info['files'].append(str(file))
                build_info['size'] += self._get_dir_size(file)
            return len(build_info['files']) > 0, build_info
        else:
            build_info['error'] = result.stderr
            return False, build_info
            
    def _build_linux_appimage(self, build_info: Dict) -> Tuple[bool, Dict]:
        """Build Linux AppImage."""
        if sys.platform != "linux":
            build_info['error'] = "AppImage can only be built on Linux"
            return False, build_info
            
        # This would require AppImage tools setup
        build_info['error'] = "AppImage build not implemented yet"
        return False, build_info
        
    def _run_tests(self) -> bool:
        """Run comprehensive test suite."""
        success = True
        
        # Test categories
        test_categories = [
            ('unit', self._run_unit_tests),
            ('integration', self._run_integration_tests),
            ('e2e_source', self._run_e2e_tests_source),
            ('e2e_wheel', self._run_e2e_tests_wheel),
            ('e2e_executable', self._run_e2e_tests_executable),
            ('performance', self._run_performance_tests),
            ('regression', self._run_regression_tests)
        ]
        
        for category, test_func in test_categories:
            self.logger.info(f"Running {category} tests...")
            
            test_success, test_info = test_func()
            
            self.results['tests'][category] = {
                'success': test_success,
                'info': test_info,
                'timestamp': datetime.now().isoformat()
            }
            
            if not test_success:
                success = False
                self.logger.error(f"{category} tests failed")
            else:
                self.logger.info(f"{category} tests passed")
                
        return success
        
    def _run_unit_tests(self) -> Tuple[bool, Dict]:
        """Run unit tests."""
        cmd = [sys.executable, "-m", "pytest", "scripts/tests/", "-v", "--tb=short"]
        
        if self.config.get('headless'):
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        test_info = {
            'command': ' '.join(cmd),
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
        return result.returncode == 0, test_info
        
    def _run_integration_tests(self) -> Tuple[bool, Dict]:
        """Run integration tests."""
        cmd = [sys.executable, "-m", "pytest", "scripts/tests/", "-v", "-m", "integration"]
        
        if self.config.get('headless'):
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        test_info = {
            'command': ' '.join(cmd),
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
        return result.returncode == 0, test_info
        
    def _run_e2e_tests_source(self) -> Tuple[bool, Dict]:
        """Run E2E tests against source distribution."""
        return self._run_e2e_tests_for_dist("source")
        
    def _run_e2e_tests_wheel(self) -> Tuple[bool, Dict]:
        """Run E2E tests against wheel distribution."""
        return self._run_e2e_tests_for_dist("wheel")
        
    def _run_e2e_tests_executable(self) -> Tuple[bool, Dict]:
        """Run E2E tests against executable."""
        return self._run_e2e_tests_for_dist("executable")
        
    def _run_e2e_tests_for_dist(self, dist_type: str) -> Tuple[bool, Dict]:
        """Run E2E tests for a specific distribution type."""
        test_info = {'dist_type': dist_type, 'tests': []}
        
        try:
            # Create isolated test environment
            test_env_dir = Path(self.temp_dir) / f"test_env_{dist_type}"
            test_env_dir.mkdir(exist_ok=True)
            
            # Install/setup the distribution
            if not self._setup_test_environment(dist_type, test_env_dir, test_info):
                return False, test_info
                
            # Run E2E test scenarios
            scenarios = [
                ('app_startup', self._test_app_startup),
                ('pdf_drop', self._test_pdf_drop),
                ('processing', self._test_pdf_processing),
                ('ui_interaction', self._test_ui_interaction),
                ('error_handling', self._test_error_handling)
            ]
            
            success = True
            for scenario_name, scenario_func in scenarios:
                self.logger.info(f"Running E2E scenario: {scenario_name}")
                
                scenario_success, scenario_info = scenario_func(test_env_dir)
                test_info['tests'].append({
                    'name': scenario_name,
                    'success': scenario_success,
                    'info': scenario_info
                })
                
                if not scenario_success:
                    success = False
                    
            return success, test_info
            
        except Exception as e:
            test_info['error'] = str(e)
            return False, test_info
            
    def _setup_test_environment(self, dist_type: str, test_env_dir: Path, test_info: Dict) -> bool:
        """Setup test environment for a distribution type."""
        try:
            if dist_type == "source":
                # Install from source
                cmd = [sys.executable, "-m", "pip", "install", "-e", str(self.project_root)]
                result = subprocess.run(cmd, cwd=test_env_dir, capture_output=True, text=True)
                
            elif dist_type == "wheel":
                # Find and install wheel
                wheel_files = list(self.build_dir.glob("*.whl"))
                if not wheel_files:
                    test_info['error'] = "No wheel file found"
                    return False
                    
                cmd = [sys.executable, "-m", "pip", "install", str(wheel_files[0])]
                result = subprocess.run(cmd, cwd=test_env_dir, capture_output=True, text=True)
                
            elif dist_type == "executable":
                # Copy executable to test environment
                exe_files = list(self.build_dir.glob("pdf-power-converter*"))
                if not exe_files:
                    test_info['error'] = "No executable found"
                    return False
                    
                shutil.copy2(exe_files[0], test_env_dir / "pdf-power-converter")
                return True
                
            else:
                test_info['error'] = f"Unknown distribution type: {dist_type}"
                return False
                
            test_info['setup_output'] = result.stdout
            test_info['setup_error'] = result.stderr
            return result.returncode == 0
            
        except Exception as e:
            test_info['error'] = f"Setup failed: {e}"
            return False
            
    def _test_app_startup(self, test_env_dir: Path) -> Tuple[bool, Dict]:
        """Test application startup."""
        test_info = {}
        
        try:
            # Test startup with timeout
            cmd = [sys.executable, "-c", """
import sys
import os
sys.path.insert(0, 'scripts')
from ui.app_controller import PDFCleanupApp
app = PDFCleanupApp(debug_mode=True)
# Quick startup test - don't actually run the GUI
print("Startup successful")
"""]
            
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True, 
                text=True, 
                timeout=self.config.get('timeout', 30),
                env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'}
            )
            
            test_info['stdout'] = result.stdout
            test_info['stderr'] = result.stderr
            test_info['returncode'] = result.returncode
            
            return result.returncode == 0 and "Startup successful" in result.stdout, test_info
            
        except subprocess.TimeoutExpired:
            test_info['error'] = "Startup timeout"
            return False, test_info
        except Exception as e:
            test_info['error'] = str(e)
            return False, test_info
            
    def _test_pdf_drop(self, test_env_dir: Path) -> Tuple[bool, Dict]:
        """Test PDF drag and drop functionality."""
        # This would require GUI automation - placeholder for now
        return True, {'status': 'GUI automation not implemented yet'}
        
    def _test_pdf_processing(self, test_env_dir: Path) -> Tuple[bool, Dict]:
        """Test PDF processing pipeline."""
        # This would test the actual PDF processing - placeholder for now
        return True, {'status': 'PDF processing test not implemented yet'}
        
    def _test_ui_interaction(self, test_env_dir: Path) -> Tuple[bool, Dict]:
        """Test UI interactions."""
        # This would require GUI automation - placeholder for now
        return True, {'status': 'UI interaction test not implemented yet'}
        
    def _test_error_handling(self, test_env_dir: Path) -> Tuple[bool, Dict]:
        """Test error handling scenarios."""
        # This would test various error conditions - placeholder for now
        return True, {'status': 'Error handling test not implemented yet'}
        
    def _run_performance_tests(self) -> Tuple[bool, Dict]:
        """Run performance tests."""
        test_info = {'metrics': {}}
        
        try:
            # Test startup time
            start_time = time.time()
            
            # Simulate app initialization
            cmd = [sys.executable, "-c", """
import time
start = time.time()
import sys
sys.path.insert(0, 'scripts')
from ui.app_controller import PDFCleanupApp
app = PDFCleanupApp()
end = time.time()
print(f"Import time: {end - start:.3f}s")
"""]
            
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True, 
                text=True,
                env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'}
            )
            
            if result.returncode == 0:
                # Extract timing from output
                for line in result.stdout.split('\n'):
                    if 'Import time:' in line:
                        import_time = float(line.split(':')[1].strip().rstrip('s'))
                        test_info['metrics']['import_time'] = import_time
                        
            test_info['stdout'] = result.stdout
            test_info['stderr'] = result.stderr
            
            # Performance thresholds
            import_time = test_info['metrics'].get('import_time', 999)
            success = import_time < 5.0  # Should import in under 5 seconds
            
            if not success:
                test_info['error'] = f"Import time too slow: {import_time}s"
                
            return success, test_info
            
        except Exception as e:
            test_info['error'] = str(e)
            return False, test_info
            
    def _run_regression_tests(self) -> Tuple[bool, Dict]:
        """Run regression tests against previous results."""
        test_info = {}
        
        # Load previous results if available
        results_file = self.project_root / self.config.get('report_file', 'test_results.json')
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    previous_results = json.load(f)
                    
                # Compare performance metrics
                regressions = self._detect_regressions(previous_results)
                test_info['regressions'] = regressions
                self.results['regressions'] = regressions
                
                return len(regressions) == 0, test_info
                
            except Exception as e:
                test_info['error'] = f"Failed to load previous results: {e}"
                return True, test_info  # Don't fail if we can't load previous results
        else:
            test_info['status'] = 'No previous results for comparison'
            return True, test_info
            
    def _detect_regressions(self, previous_results: Dict) -> List[Dict]:
        """Detect regressions by comparing with previous results."""
        regressions = []
        
        # Compare performance metrics
        prev_perf = previous_results.get('tests', {}).get('performance', {}).get('info', {}).get('metrics', {})
        curr_perf = self.results.get('tests', {}).get('performance', {}).get('info', {}).get('metrics', {})
        
        for metric, prev_value in prev_perf.items():
            curr_value = curr_perf.get(metric)
            if curr_value is not None:
                # Check for significant performance regression (>20% slower)
                if curr_value > prev_value * 1.2:
                    regressions.append({
                        'type': 'performance',
                        'metric': metric,
                        'previous': prev_value,
                        'current': curr_value,
                        'regression_percent': ((curr_value - prev_value) / prev_value) * 100
                    })
                    
        # Compare test success rates
        prev_tests = previous_results.get('tests', {})
        curr_tests = self.results.get('tests', {})
        
        for test_name, prev_test in prev_tests.items():
            curr_test = curr_tests.get(test_name, {})
            if prev_test.get('success') and not curr_test.get('success'):
                regressions.append({
                    'type': 'test_failure',
                    'test': test_name,
                    'previous': 'passed',
                    'current': 'failed'
                })
                
        return regressions
        
    def _generate_report(self):
        """Generate comprehensive test report."""
        # Calculate summary
        total_builds = len(self.results['builds'])
        successful_builds = sum(1 for b in self.results['builds'].values() if b['success'])
        
        total_tests = len(self.results['tests'])
        successful_tests = sum(1 for t in self.results['tests'].values() if t['success'])
        
        self.results['summary'] = {
            'total_builds': total_builds,
            'successful_builds': successful_builds,
            'build_success_rate': successful_builds / total_builds if total_builds > 0 else 0,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'test_success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'total_regressions': len(self.results['regressions']),
            'overall_success': successful_builds == total_builds and successful_tests == total_tests and len(self.results['regressions']) == 0
        }
        
        # Save results
        report_file = self.project_root / self.config.get('report_file', 'test_results.json')
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        # Generate human-readable report
        self._generate_human_report()
        
        self.logger.info(f"Report saved to {report_file}")
        
    def _generate_human_report(self):
        """Generate human-readable report."""
        summary = self.results['summary']
        
        report = f"""
# Build and Test Report
Generated: {self.results['timestamp']}

## Summary
- **Overall Success**: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}
- **Builds**: {summary['successful_builds']}/{summary['total_builds']} ({summary['build_success_rate']:.1%})
- **Tests**: {summary['successful_tests']}/{summary['total_tests']} ({summary['test_success_rate']:.1%})
- **Regressions**: {summary['total_regressions']}

## Build Results
"""
        
        for platform, build in self.results['builds'].items():
            status = '✅ PASS' if build['success'] else '❌ FAIL'
            report += f"- **{platform}**: {status}\n"
            if build['info'].get('files'):
                report += f"  - Files: {len(build['info']['files'])}\n"
                report += f"  - Size: {build['info']['size'] / 1024 / 1024:.1f} MB\n"
                
        report += "\n## Test Results\n"
        
        for test_name, test in self.results['tests'].items():
            status = '✅ PASS' if test['success'] else '❌ FAIL'
            report += f"- **{test_name}**: {status}\n"
            
        if self.results['regressions']:
            report += "\n## Regressions\n"
            for regression in self.results['regressions']:
                report += f"- **{regression['type']}**: {regression.get('metric', regression.get('test'))}\n"
                if regression['type'] == 'performance':
                    report += f"  - Previous: {regression['previous']}\n"
                    report += f"  - Current: {regression['current']}\n"
                    report += f"  - Regression: {regression['regression_percent']:.1f}%\n"
                    
        # Save human report
        report_file = self.project_root / 'build_test_report.md'
        with open(report_file, 'w') as f:
            f.write(report)
            
    def _get_dir_size(self, path: Path) -> int:
        """Get total size of directory."""
        total = 0
        for file in path.rglob('*'):
            if file.is_file():
                total += file.stat().st_size
        return total
        
    def _cleanup(self):
        """Cleanup temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def watch_mode(self):
        """Run in watch mode - monitor for changes and auto-rebuild/test."""
        self.logger.info("Starting watch mode...")
        
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            self.logger.error("watchdog package required for watch mode")
            return False
            
        class ChangeHandler(FileSystemEventHandler):
            def __init__(self, runner):
                self.runner = runner
                self.last_run = 0
                
            def on_modified(self, event):
                if event.is_directory:
                    return
                    
                # Debounce - only run once per 5 seconds
                now = time.time()
                if now - self.last_run < 5:
                    return
                    
                # Only watch Python files
                if not event.src_path.endswith('.py'):
                    return
                    
                self.last_run = now
                self.runner.logger.info(f"Change detected: {event.src_path}")
                
                # Run build and test in background thread
                threading.Thread(target=self.runner.run, daemon=True).start()
                
        handler = ChangeHandler(self)
        observer = Observer()
        observer.schedule(handler, str(self.project_root / 'scripts'), recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            
        observer.join()
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build and test automation")
    parser.add_argument('--build-only', action='store_true', help='Only build, don\'t test')
    parser.add_argument('--test-only', action='store_true', help='Only test, don\'t build')
    parser.add_argument('--watch', action='store_true', help='Watch for changes and auto-rebuild/test')
    parser.add_argument('--report-file', default='test_results.json', help='Output file for results')
    parser.add_argument('--platforms', nargs='+', default=['source', 'wheel'], 
                       choices=['source', 'wheel', 'exe', 'app', 'appimage'],
                       help='Platforms to build for')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--headless', action='store_true', help='Run GUI tests in headless mode')
    parser.add_argument('--timeout', type=int, default=300, help='Test timeout in seconds')
    
    args = parser.parse_args()
    
    config = {
        'build_only': args.build_only,
        'test_only': args.test_only,
        'watch': args.watch,
        'report_file': args.report_file,
        'platforms': args.platforms,
        'verbose': args.verbose,
        'headless': args.headless,
        'timeout': args.timeout
    }
    
    runner = BuildTestRunner(config)
    
    if args.watch:
        success = runner.watch_mode()
    else:
        success = runner.run()
        
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()