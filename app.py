from flask import Flask, render_template, request, jsonify
import mysql.connector
from contextlib import contextmanager

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'sql12.freemysqlhosting.net',
    'user': 'sql12758235',
    'password': 'ZHbrlmdRv1',
    'database': 'sql12758235'
}

@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    try:
        yield conn
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/specifications')
def specifications():
    phone_ids = request.args.getlist('phones')
    if not phone_ids:
        return "No phones selected", 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            placeholders = ', '.join(['%s'] * len(phone_ids))
            query = f"SELECT * FROM spec WHERE index_num IN ({placeholders})"
            cursor.execute(query, phone_ids)
            phones = cursor.fetchall()
            cursor.close()
            
            if not phones:
                return "No phones found", 404
                
            return render_template('specifications.html', phones=phones)
    except Exception as e:
        app.logger.error(f"Database error: {str(e)}")
        return "An error occurred while fetching phone specifications", 500

@app.route('/compare')
def compare():
    phone_ids = request.args.getlist('phones')
    if not phone_ids or len(phone_ids) != 2:
        return "Please select exactly two phones to compare", 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            placeholders = ', '.join(['%s'] * len(phone_ids))
            query = f"SELECT * FROM spec WHERE index_num IN ({placeholders})"
            cursor.execute(query, phone_ids)
            phones = cursor.fetchall()
            cursor.close()
            
            if not phones or len(phones) != 2:
                return "Selected phones not found", 404
                
            return render_template('compare.html', phones=phones)
    except Exception as e:
        app.logger.error(f"Database error: {str(e)}")
        return "An error occurred while comparing phones", 500

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        if not data or 'preferences' not in data or 'budget' not in data or 'priority_list' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400

        user_preferences = data['preferences']
        budget = data['budget']
        priority_list = data['priority_list']

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM spec WHERE b_Price <= %s", (budget,))
            phones = cursor.fetchall()
            cursor.close()

            if not phones:
                return jsonify({
                    'success': True,
                    'recommendations': []
                })

            # Calculate scores exactly like the original logic
            for phone in phones:
                phone['Design_diff'] = (int(phone['design']) - user_preferences[0]) * priority_list[0]
                phone['Display_diff'] = (int(phone['display']) - user_preferences[1]) * priority_list[1]
                phone['Software_diff'] = (int(phone['software']) - user_preferences[2]) * priority_list[2]
                phone['Performance_diff'] = (int(phone['performance']) - user_preferences[3]) * priority_list[3]
                phone['Battery_diff'] = (int(phone['battery_life']) - user_preferences[4]) * priority_list[4]
                phone['Camera_diff'] = (int(phone['camera']) - user_preferences[5]) * priority_list[5]
                
                phone['main_diff'] = (
                    phone['Camera_diff'] + 
                    phone['Performance_diff'] + 
                    phone['Display_diff'] + 
                    phone['Battery_diff'] + 
                    phone['Software_diff'] + 
                    phone['Design_diff']
                )

            # Sort by main_diff in descending order (higher scores first) like the original
            phones.sort(key=lambda x: x['main_diff'], reverse=True)
            top_phones = phones[:2]

            return jsonify({
                'success': True,
                'recommendations': top_phones
            })

    except Exception as e:
        app.logger.error(f"Recommendation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while generating recommendations'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)