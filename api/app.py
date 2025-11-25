from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
CORS(app, resources={r"/api/*": {"origins": "*"}})


game_sessions = {}

QUIZ_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct": 2,
        "category": "Geography"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct": 1,
        "category": "Science"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "correct": 1,
        "category": "Literature"
    },
    {
        "question": "What is 15 × 8?",
        "options": ["110", "120", "130", "140"],
        "correct": 1,
        "category": "Mathematics"
    },
    {
        "question": "Which gas do plants absorb from the atmosphere?",
        "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        "correct": 2,
        "category": "Science"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
        "correct": 3,
        "category": "Geography"
    },
    {
        "question": "In which year did World War II end?",
        "options": ["1943", "1944", "1945", "1946"],
        "correct": 2,
        "category": "History"
    },
    {
        "question": "What is the chemical symbol for gold?",
        "options": ["Go", "Gd", "Au", "Ag"],
        "correct": 2,
        "category": "Science"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Michelangelo"],
        "correct": 2,
        "category": "Art"
    },
    {
        "question": "What is the smallest prime number?",
        "options": ["0", "1", "2", "3"],
        "correct": 2,
        "category": "Mathematics"
    },
    {
        "question": "Which continent is the largest by area?",
        "options": ["Africa", "Asia", "North America", "Europe"],
        "correct": 1,
        "category": "Geography"
    },
    {
        "question": "What is the speed of light?",
        "options": ["300,000 km/s", "150,000 km/s", "450,000 km/s", "200,000 km/s"],
        "correct": 0,
        "category": "Science"
    },
    {
        "question": "Who invented the telephone?",
        "options": ["Thomas Edison", "Nikola Tesla", "Alexander Graham Bell", "Benjamin Franklin"],
        "correct": 2,
        "category": "History"
    },
    {
        "question": "What is the main ingredient in guacamole?",
        "options": ["Tomato", "Avocado", "Cucumber", "Lettuce"],
        "correct": 1,
        "category": "General Knowledge"
    },
    {
        "question": "How many continents are there?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,
        "category": "Geography"
    }
]

# Root endpoint


QUIZ GAME API ENDPOINTS

@app.route('/api/quiz/start', methods=['POST'])
def start_quiz():
    """Initialize a new quiz game session"""
    try:
        data = request.get_json() or {}
        player_name = data.get('player_name', 'Anonymous')
        num_questions = data.get('num_questions', 10)
        
        session_id = f"quiz_{datetime.now().timestamp()}"
       
        questions = random.sample(QUIZ_QUESTIONS, min(num_questions, len(QUIZ_QUESTIONS)))
        
       
        game_sessions[session_id] = {
            'game_type': 'quiz',
            'player_name': player_name,
            'questions': questions,
            'current_question': 0,
            'score': 0,
            'correct_answers': 0,
            'started_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'total_questions': len(questions),
            'message': 'Quiz started successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to start quiz: {str(e)}'}), 500


@app.route('/api/quiz/question/<session_id>', methods=['GET'])
def get_question(session_id):
    """Get the current question for a quiz session"""
    try:
        if session_id not in game_sessions:
            return jsonify({'success': False, 'error': 'Invalid session'}), 404
        
        session_data = game_sessions[session_id]
        current_idx = session_data['current_question']
        
        if current_idx >= len(session_data['questions']):
            return jsonify({
                'success': True,
                'completed': True,
                'message': 'Quiz completed'
            })
        
        question_data = session_data['questions'][current_idx]
        
        return jsonify({
            'success': True,
            'completed': False,
            'question_number': current_idx + 1,
            'total_questions': len(session_data['questions']),
            'question': question_data['question'],
            'options': question_data['options'],
            'category': question_data['category'],
            'score': session_data['score']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to load question: {str(e)}'}), 500


@app.route('/api/quiz/answer', methods=['POST'])
def submit_answer():
    """Submit an answer for the current question"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        selected_option = data.get('selected_option')
        
        if session_id not in game_sessions:
            return jsonify({'success': False, 'error': 'Invalid session'}), 404
        
        session_data = game_sessions[session_id]
        current_idx = session_data['current_question']
        
        if current_idx >= len(session_data['questions']):
            return jsonify({'success': False, 'error': 'No more questions'}), 400
        
        question_data = session_data['questions'][current_idx]
        correct_answer = question_data['correct']
        is_correct = (selected_option == correct_answer)
        
    
        if is_correct:
            session_data['score'] += 10
            session_data['correct_answers'] += 1
        
        session_data['current_question'] += 1
        
        
        is_complete = session_data['current_question'] >= len(session_data['questions'])
        
        response_data = {
            'success': True,
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'explanation': question_data['options'][correct_answer],
            'current_score': session_data['score'],
            'quiz_complete': is_complete
        }
        
      
        if is_complete:
            response_data['final_score'] = session_data['score']
            response_data['correct_answers'] = session_data['correct_answers']
            response_data['total_questions'] = len(session_data['questions'])
            response_data['percentage'] = (session_data['correct_answers'] / len(session_data['questions'])) * 100
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to submit answer: {str(e)}'}), 500


@app.route('/api/quiz/stats/<session_id>', methods=['GET'])
def get_quiz_stats(session_id):
    """Get statistics for a quiz session"""
    try:
        if session_id not in game_sessions:
            return jsonify({'success': False, 'error': 'Invalid session'}), 404
        
        session_data = game_sessions[session_id]
        
        return jsonify({
            'success': True,
            'score': session_data['score'],
            'correct_answers': session_data['correct_answers'],
            'total_questions': len(session_data['questions']),
            'current_question': session_data['current_question'],
            'percentage': (session_data['correct_answers'] / len(session_data['questions'])) * 100 if len(session_data['questions']) > 0 else 0
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get stats: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Quiz API is running successfully',
        'active_sessions': len(game_sessions),
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500



if __name__ != '__main__':
  
    app.debug = False
else:
   
    app.run(debug=True, host='0.0.0.0', port=5000)
