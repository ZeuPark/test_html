from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import datetime
import os

# Import your ML model here
# Example: from your_model import YourMLModel

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Initialize your ML model
# model = YourMLModel()

# Sample data (in a real app, this would be a database)
questions_db = [
    {
        "id": 1,
        "title": "How do I reset my smartphone password?",
        "category": "Technology",
        "content": "I forgot my phone password and can't access my device. What should I do?",
        "answers": 3,
        "timestamp": "2 hours ago",
        "author": "TechHelper"
    },
    {
        "id": 2,
        "title": "What documents do I need for international travel?",
        "category": "Travel",
        "content": "Planning a trip abroad. What paperwork is essential?",
        "answers": 7,
        "timestamp": "4 hours ago",
        "author": "Traveler123"
    },
    {
        "id": 3,
        "title": "How often should I visit my doctor for checkups?",
        "category": "Health",
        "content": "What's the recommended frequency for routine medical checkups?",
        "answers": 5,
        "timestamp": "1 day ago",
        "author": "HealthyLiving"
    }
]

categories_db = [
    {"name": "Travel & Vacation", "icon": "✈️", "count": 125, "id": "travel"},
    {"name": "Legal Advice", "icon": "⚖️", "count": 89, "id": "legal"},
    {"name": "Health & Wellness", "icon": "🏥", "count": 203, "id": "health"},
    {"name": "Technology Help", "icon": "💻", "count": 156, "id": "technology"},
    {"name": "Finance & Money", "icon": "💰", "count": 67, "id": "finance"},
    {"name": "Hobbies & Crafts", "icon": "🎨", "count": 92, "id": "hobbies"}
]

@app.route('/')
def home():
    return render_template('home_template.html')

@app.route('/categories')
def categories():
    return render_template('categories.html', categories=categories_db)

@app.route('/questions')
def questions():
    return render_template('questions.html', questions=questions_db)

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Handle question submission and ML model inference"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        category = data.get('category', 'General')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Here's where you'd use your ML model
        # Example:
        # answer = model.generate_answer(question, category)
        
        # For now, we'll return a sample response
        sample_answer = f"Thank you for your question about {category.lower()}. Here's a helpful response based on our AI model: [Your ML model would generate an answer here based on the question: '{question}']. This is where your trained model would provide a personalized, accurate response."
        
        # Save question to database (in real app)
        new_question = {
            "id": len(questions_db) + 1,
            "title": question,
            "category": category,
            "content": question,
            "answers": 1,  # Our AI answer
            "timestamp": "Just now",
            "author": "You",
            "ai_answer": sample_answer
        }
        
        questions_db.append(new_question)
        
        return jsonify({
            'success': True,
            'answer': sample_answer,
            'question_id': new_question['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions')
def get_questions():
    """API endpoint to get all questions"""
    return jsonify(questions_db)

@app.route('/api/questions/<int:question_id>')
def get_question(question_id):
    """API endpoint to get a specific question"""
    question = next((q for q in questions_db if q['id'] == question_id), None)
    if question:
        return jsonify(question)
    return jsonify({'error': 'Question not found'}), 404

@app.route('/api/categories')
def get_categories():
    """API endpoint to get all categories"""
    return jsonify(categories_db)

@app.route('/api/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # Simple search in questions
    results = []
    for question in questions_db:
        if (query.lower() in question['title'].lower() or 
            query.lower() in question['content'].lower()):
            results.append(question)
    
    return jsonify(results)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("🚀 Starting Q&A Platform Server...")
    print("📝 Place your ML model integration in the ask_question() function")
    print("🌐 Visit: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)