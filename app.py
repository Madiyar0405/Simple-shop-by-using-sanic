from sanic import Sanic, response
from jinja2 import Environment, FileSystemLoader

import asyncpg

app = Sanic(__name__)

env = Environment(loader=FileSystemLoader('templates'))

DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'my_store',
    'user': 'postgres',
    'password': 'rootroot'
}

async def create_db_connection():
    return await asyncpg.connect(**DATABASE_CONFIG)




@app.route('/add-to-cart', methods=['POST'])
async def add_to_cart(request):
    data = request.form
    user_id = data.get('user_id')
    product_name = data.get('product_name')
    price = data.get('price')

    conn = await create_db_connection()
    await conn.execute('INSERT INTO cart (user_id, product_name, price) VALUES ($1, $2, $3)', user_id, product_name, price)
    await conn.close()

    return response.redirect('/profile')

@app.route('/profile')
async def profile(request):
    template = env.get_template('./profile.html')
    user_id = request.args.get('user_id')
    
    conn = await create_db_connection()
    cart = await conn.fetch('SELECT product_name, price FROM cart WHERE user_id = $1', user_id)
    await conn.close()

    return response.html(template.render(cart=cart))

@app.route('/products')
async def products(request):
    template = env.get_template('./products.html')
    return response.html(template.render())

@app.route('/register', methods=['GET', 'POST'])
async def register_user(request):
    if request.method == 'GET':
        template = env.get_template('./register.html')
        return response.html(template.render())

    data = request.form
    username = data.get('username')
    password = data.get('password')

    conn = await create_db_connection()
    await conn.execute('INSERT INTO users (username, password) VALUES ($1, $2)', username, password)
    await conn.close()

    return response.redirect('./login')  

@app.route('/login', methods=['GET', 'POST'])
async def login_user(request):
    if request.method == 'GET':
        template = env.get_template('./login.html')
        return response.html(template.render())

    data = request.form
    username = data.get('username')
    password = data.get('password')

    conn = await create_db_connection()
    user_record = await conn.fetchrow('SELECT * FROM users WHERE username = $1', username)
    await conn.close()

    if user_record and password == user_record['password']:
        return response.redirect('/products')
    else:
        return response.redirect('/failure')

@app.route('/success')
async def success(request):
    return response.text('Login successful')

@app.route('/failure')
async def failure(request):
    return response.text('Invalid username or password', status=401)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
