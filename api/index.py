from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import sys
import json
import traceback

app = Flask(__name__)
CORS(app)

EXECUTION_TIMEOUT = 10

@app.route('/api/run', methods=['POST', 'OPTIONS'])
def run_code():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        code = data.get('code', '')
        user_input = data.get('input', '')
        
        if not code.strip():
            return jsonify({'error': 'No code provided'}), 400
        
        # Create wrapper that suppresses input prompts
        wrapper_code = f'''
import builtins
import sys
import json

# Save original input
_original_input = builtins.input

# Create custom input that doesn't print prompt
def _custom_input(prompt=''):
    return _original_input()

# Replace input function
builtins.input = _custom_input

# Execute user code
{code}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(wrapper_code)
            temp_file = f.name
        
        try:
            process = subprocess.Popen(
                [sys.executable, temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            try:
                stdout, stderr = process.communicate(input=user_input, timeout=EXECUTION_TIMEOUT)
                
                if stderr:
                    return jsonify({
                        'output': stderr,
                        'error': True
                    })
                else:
                    return jsonify({
                        'output': stdout if stdout.strip() else 'Code executed successfully',
                        'error': False
                    })
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return jsonify({
                    'output': f'Error: Code execution timed out',
                    'error': True
                })
                
        except Exception as e:
            return jsonify({
                'output': f'Error: {str(e)}',
                'error': True
            })
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit', methods=['POST'])
def submit_solution():
    try:
        data = request.json
        code = data.get('code', '')
        problem_id = data.get('problemId')
        test_cases = data.get('testCases', [])
        
        if not code.strip():
            return jsonify({'error': 'No code provided'}), 400
        
        results = []
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            # Create wrapper with test case input
            test_code = f'''
import builtins
import sys
import io

# Capture output
output_capture = io.StringIO()
sys.stdout = output_capture

# Save original input
_original_input = builtins.input
input_values = iter({test_case['input'].split() if test_case['input'] else []})

def _custom_input(prompt=''):
    try:
        return next(input_values)
    except StopIteration:
        return ""

builtins.input = _custom_input

# Execute user code
{code}

# Get captured output
output = output_capture.getvalue().strip()

# Print the actual output for comparison
print(output)
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(test_code)
                temp_file = f.name
            
            try:
                process = subprocess.Popen(
                    [sys.executable, temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                
                try:
                    stdout, stderr = process.communicate(timeout=EXECUTION_TIMEOUT)
                    
                    actual_output = stdout.strip()
                    expected_output = test_case['expected'].strip()
                    
                    # Compare outputs
                    passed = actual_output == expected_output
                    
                    results.append({
                        'testCase': i + 1,
                        'input': test_case['input'],
                        'expected': expected_output,
                        'output': actual_output,
                        'passed': passed
                    })
                    
                    if not passed:
                        all_passed = False
                        
                except subprocess.TimeoutExpired:
                    process.kill()
                    results.append({
                        'testCase': i + 1,
                        'input': test_case['input'],
                        'expected': test_case['expected'],
                        'output': 'Timeout',
                        'passed': False
                    })
                    all_passed = False
                    
            except Exception as e:
                results.append({
                    'testCase': i + 1,
                    'input': test_case['input'],
                    'expected': test_case['expected'],
                    'output': f'Error: {str(e)}',
                    'passed': False
                })
                all_passed = False
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        return jsonify({
            'success': all_passed,
            'results': results,
            'totalTests': len(test_cases),
            'passedTests': sum(1 for r in results if r['passed'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/problems', methods=['GET'])
def get_problems():
    try:
        with open('data/problems.json', 'r') as f:
            problems_data = json.load(f)
        return jsonify(problems_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)