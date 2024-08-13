from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import json
import random
import openai
import os


app = Flask(__name__)  # Исправлено 'name' на '__name__'
app.secret_key = 'supersecretkey'  # Секретный ключ для сессий

# Фиксируем seed для сохранения постоянства рандомных значений
random.seed(42)
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

# Загрузка данных из JSON файла
with open('data/tasks.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Главная страница с кнопкой генерации
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/math.html')
def main():
    return render_template('math.html')

# Функция для генерации варианта
@app.route('/generate')
def generate_variant():
    variant = {}

    for task_number in sorted(tasks.keys(), key=int):
        task_variants = tasks[task_number]
        selected_variant = random.choice(task_variants)
        variant[task_number] = selected_variant
    
    session['generated_variant'] = variant  # Сохраняем сгенерированный вариант в сессии
    
    return redirect(url_for('show_variant'))

@app.route('/variant')
def show_variant():
    variant = session.get('generated_variant')
    if not variant:
        return redirect(url_for('index'))
    return render_template('variant.html', variant=variant)

# Функция для проверки ответов пользователя
@app.route('/check_answers', methods=['POST'])
def check_answers():
    variant = session.get('generated_variant')
    if not variant:
        return redirect(url_for('index'))  

    user_answers = {}
    correct_answers = {}
    results = {}
    solutions = {}

    for task_number, task in variant.items():
        user_answer = request.form.get(f'answer_{task_number}')
        correct_answer = task['answer']
        user_answers[task_number] = user_answer
        correct_answers[task_number] = correct_answer
        results[task_number] = (user_answer == correct_answer)
        solutions[task_number] = task['solution_image']  # Добавляем решение

    return render_template('results.html', user_answers=user_answers, correct_answers=correct_answers, results=results, solutions=solutions)

@app.route('/chat.html', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')
    
    if request.method == 'POST':
        data = request.get_json()
        user_message = data.get('message')

        # Используем GPT-4 модель
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Убедитесь, что используете корректное название модели
            messages=[
                {"role": "system", "content": "You are a helpful math teacher. Help me with math."},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Получаем ответ от модели
        gpt_message = response.choices[0].message['content']
        
        return jsonify({'message': gpt_message})
    

if __name__ == '__main__':
    app.run(debug=True)
#http://127.0.0.1:5000/