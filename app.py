from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import datetime
import os

# Import your ML model here
# Example: from your_model import YourMLModel

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Initialize your ML model (load once for better performance)
# model = YourMLModel()

# Sample data (in production, replace with a real database)
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
    },
    {
        "id": 4,
        "title": "How do I protect myself from online scams?",
        "category": "Technology",
        "content": "I keep getting suspicious emails and calls. How can I stay safe?",
        "answers": 8,
        "timestamp": "3 hours ago",
        "author": "SafetyFirst"
    },
    {
        "id": 5,
        "title": "What's the best way to save for retirement?",
        "category": "Finance",
        "content": "I'm 50 and want to make sure I have enough saved for retirement.",
        "answers": 12,
        "timestamp": "1 day ago",
        "author": "PlanningAhead"
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
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        question = data.get('question', '').strip()
        category = data.get('category', 'General')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if len(question) > 1000:  # Reasonable limit
            return jsonify({'error': 'Question too long (max 1000 characters)'}), 400
        
        # HERE'S WHERE YOU INTEGRATE YOUR ML MODEL
        # Replace this sample response with your actual model inference
        
        # Example for different types of models:
        
        # Option 1: Hugging Face Transformers
        # answer = model(f"Answer this {category.lower()} question: {question}")
        
        # Option 2: OpenAI API
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": f"Answer this {category} question: {question}"}]
        # )
        # answer = response.choices[0].message.content
        
        # Option 3: Custom PyTorch/TensorFlow model
        # answer = model.generate_answer(question, category)
        
        # Sample response (replace with your model)
        sample_answers = {
            "Technology": f"For your technology question about '{question}', here are some helpful steps: First, try restarting your device. If that doesn't work, check for software updates. You can also contact customer support for your specific device. Always keep your passwords secure and consider using a password manager.",
            
            "Health": f"Regarding your health question '{question}', it's always best to consult with your healthcare provider for personalized advice. In general, maintaining a healthy lifestyle with regular exercise, balanced nutrition, and adequate sleep is important. Don't hesitate to schedule regular check-ups with your doctor.",
            
            "Travel": f"For your travel question '{question}', here's what I recommend: Check passport expiration dates (should be valid 6+ months), research visa requirements for your destination, notify your bank of travel plans, and consider travel insurance. The State Department website has current travel advisories.",
            
            "Legal": f"Concerning your legal question '{question}', I'd recommend consulting with a qualified attorney for specific legal advice. Many areas have legal aid societies that offer free or low-cost consultations. You can also check your state's bar association website for referrals.",
            
            "Finance": f"For your financial question '{question}', consider speaking with a financial advisor who can provide personalized guidance. Generally, it's wise to have an emergency fund, diversify investments, and regularly review your financial goals. Many banks offer free financial planning consultations.",
            
            "General": f"Thank you for your question '{question}'. Here's some general guidance: Research from reliable sources, consult with experts when needed, and don't hesitate to ask follow-up questions. If this is urgent, please contact the appropriate professionals or services."
        }
        
        answer = sample_answers.get(category, sample_answers["General"])
        
        # Save question to database (in real app, use proper database)
        new_question = {
            "id": len(questions_db) + 1,
            "title": question,
            "category": category,
            "content": question,
            "answers": 1,  # Our AI answer counts as 1
            "timestamp": "Just now",
            "author": "You",
            "ai_answer": answer
        }
        
        questions_db.append(new_question)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'question_id': new_question['id'],
            'category': category
        })
        
    except Exception as e:
        app.logger.error(f"Error in ask_question: {str(e)}")
        return jsonify({'error': 'An error occurred processing your question. Please try again.'}), 500

@app.route('/api/questions')
def get_questions():
    """API endpoint to get all questions"""
    try:
        # In production, add pagination
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Simple pagination
        paginated_questions = questions_db[offset:offset + limit]
        
        return jsonify({
            'questions': paginated_questions,
            'total': len(questions_db),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        app.logger.error(f"Error in get_questions: {str(e)}")
        return jsonify({'error': 'Failed to fetch questions'}), 500

@app.route('/api/questions/<int:question_id>')
def get_question(question_id):
    """API endpoint to get a specific question"""
    try:
        question = next((q for q in questions_db if q['id'] == question_id), None)
        if question:
            return jsonify(question)
        return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        app.logger.error(f"Error in get_question: {str(e)}")
        return jsonify({'error': 'Failed to fetch question'}), 500

@app.route('/api/categories')
def get_categories():
    """API endpoint to get all categories"""
    try:
        return jsonify(categories_db)
    except Exception as e:
        app.logger.error(f"Error in get_categories: {str(e)}")
        return jsonify({'error': 'Failed to fetch categories'}), 500

@app.route('/api/search')
def search():
    """Search functionality with better error handling"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])
        
        if len(query) > 200:  # Reasonable search limit
            return jsonify({'error': 'Search query too long'}), 400
        
        # Simple search in questions (in production, use proper search engine)
        results = []
        query_lower = query.lower()
        
        for question in questions_db:
            if (query_lower in question['title'].lower() or 
                query_lower in question['content'].lower() or
                query_lower in question['category'].lower()):
                results.append(question)
        
        # Limit results
        results = results[:50]  # Max 50 results
        
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"Error in search: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# Create required directories
def create_directories():
    directories = ['templates', 'static']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

if __name__ == '__main__':
    create_directories()
    
    # Get port from environment variable (required for cloud deployment)
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Q&A Platform Server...")
    print(f"📝 Integrate your ML model in the ask_question() function")
    print(f"🌐 Server will run on port {port}")
    
    if DEBUG:
        print("🔧 Running in DEBUG mode")
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        print("🚀 Running in PRODUCTION mode")
        app.run(debug=False, host='0.0.0.0', port=port)