from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
from decimal import Decimal
import os
import random

app = Flask(__name__)
CORS(app)

# MySQL数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '4wv79nd4v3',
    'database': 'factory',
    'port': 3306
}


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


app.json_encoder = DecimalEncoder


def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None


# ==================== 主页路由 ====================
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>工厂库存管理系统 - API服务</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 20px; font-family: Arial, sans-serif; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #0d6efd; }
            .btn-group { margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mt-4">🏭 工厂氟胶垫片库存管理系统</h1>
            <p class="lead">✅ Flask API服务正在运行</p>

            <div class="row">
                <div class="col-md-6">
                    <div class="endpoint">
                        <h4>📡 系统状态</h4>
                        <p><strong>服务地址:</strong> http://127.0.0.1:5000</p>
                        <p><strong>数据库:</strong> factory_inventory_db</p>
                        <p><strong>状态:</strong> <span class="badge bg-success">运行中</span></p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="endpoint">
                        <h4>🔗 快速链接</h4>
                        <div class="btn-group-vertical w-100">
                            <a href="/api/test" class="btn btn-outline-primary mb-2">测试API</a>
                            <a href="/api/products" class="btn btn-outline-primary mb-2">产品列表</a>
                            <a href="http://localhost:8000/index.html" class="btn btn-outline-success mb-2" target="_blank">前端界面</a>
                        </div>
                    </div>
                </div>
            </div>

            <div class="endpoint">
                <h4>📋 API端点列表</h4>
                <table class="table table-sm">
                    <thead>
                        <tr><th>方法</th><th>端点</th><th>描述</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>GET</td><td><code>/api/test</code></td><td>测试API连接</td></tr>
                        <tr><td>GET</td><td><code>/api/products</code></td><td>获取产品列表</td></tr>
                        <tr><td>POST</td><td><code>/api/products</code></td><td>创建新产品</td></tr>
                        <tr><td>GET</td><td><code>/api/products/&lt;id&gt;</code></td><td>获取单个产品</td></tr>
                        <tr><td>PUT</td><td><code>/api/products/&lt;id&gt;</code></td><td>更新产品</td></tr>
                        <tr><td>DELETE</td><td><code>/api/products/&lt;id&gt;</code></td><td>删除产品</td></tr>
                        <tr><td>GET</td><td><code>/api/inventory/alerts</code></td><td>获取库存预警</td></tr>
                        <tr><td>GET</td><td><code>/api/statistics/sales</code></td><td>获取销售统计</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="mt-4">
                <h5>💡 使用说明</h5>
                <ol>
                    <li>确保MySQL数据库服务正在运行</li>
                    <li>确认数据库配置正确（用户名、密码）</li>
                    <li>通过前端页面访问系统功能</li>
                    <li>所有数据变动将保存到MySQL数据库</li>
                </ol>
            </div>

            <footer class="mt-4 text-muted">
                <hr>
                <p>系统时间: {}</p>
            </footer>
        </div>
    </body>
    </html>
    '''.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


# ==================== 产品管理API ====================
@app.route('/api/test', methods=['GET'])
def test_api():
    """测试API连接和数据库连接"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return jsonify({
                "status": "success",
                "message": "API服务和数据库连接正常",
                "database": "connected",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return jsonify({
                "status": "error",
                "message": "数据库连接失败",
                "database": "disconnected"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 支持分页和筛选
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        material_type = request.args.get('material_type', '')
        status = request.args.get('status', '')

        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if material_type:
            query += " AND material_type = %s"
            params.append(material_type)
        if status:
            query += " AND status = %s"
            params.append(status)

        # 获取总数
        count_query = query.replace("SELECT *", "SELECT COUNT(*) as total")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 获取分页数据
        query += " ORDER BY product_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, params)
        products = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'data': products,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products', methods=['POST'])
def create_product():
    """创建新产品"""
    try:
        data = request.json
        print("创建产品数据:", data)

        # 验证必要字段
        required_fields = ['product_code', 'product_name', 'material_type', 'unit_price']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查产品编码是否重复
        cursor.execute("SELECT product_id FROM products WHERE product_code = %s", (data['product_code'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': '产品编码已存在'}), 400

        # 插入新产品
        query = """
            INSERT INTO products (
                product_code, product_name, category_id, specification,
                material_type, unit, unit_price, min_stock_level,
                max_stock_level, current_stock, warehouse_location, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['product_code'],
            data['product_name'],
            data.get('category_id'),
            data.get('specification', ''),
            data['material_type'],
            data.get('unit', '个'),
            float(data['unit_price']),
            int(data.get('min_stock_level', 10)),
            int(data.get('max_stock_level', 1000)),
            int(data.get('current_stock', 0)),
            data.get('warehouse_location', ''),
            data.get('status', '正常')
        )

        cursor.execute(query, values)
        product_id = cursor.lastrowid

        # 记录库存变动
        if data.get('current_stock', 0) > 0:
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    product_id, transaction_type, quantity_change,
                    quantity_before, quantity_after, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                product_id,
                '库存调整',
                int(data.get('current_stock', 0)),
                0,
                int(data.get('current_stock', 0)),
                '初始库存'
            ))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '产品创建成功',
            'product_id': product_id,
            'product_code': data['product_code']
        }), 201

    except Exception as e:
        print("创建产品错误:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取单个产品详情"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        cursor.close()
        conn.close()

        if not product:
            return jsonify({'error': '产品不存在'}), 404

        return jsonify(product)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新产品信息"""
    try:
        data = request.json

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查产品是否存在
        cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': '产品不存在'}), 404

        # 构建更新语句
        update_fields = []
        values = []

        if 'product_name' in data:
            update_fields.append("product_name = %s")
            values.append(data['product_name'])
        if 'material_type' in data:
            update_fields.append("material_type = %s")
            values.append(data['material_type'])
        if 'specification' in data:
            update_fields.append("specification = %s")
            values.append(data['specification'])
        if 'unit_price' in data:
            update_fields.append("unit_price = %s")
            values.append(float(data['unit_price']))
        if 'current_stock' in data:
            # 获取当前库存用于记录变动
            cursor.execute("SELECT current_stock FROM products WHERE product_id = %s", (product_id,))
            old_stock = cursor.fetchone()[0]
            new_stock = int(data['current_stock'])

            update_fields.append("current_stock = %s")
            values.append(new_stock)

            # 记录库存变动
            if new_stock != old_stock:
                cursor.execute("""
                    INSERT INTO inventory_transactions (
                        product_id, transaction_type, quantity_change,
                        quantity_before, quantity_after, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    product_id,
                    '库存调整',
                    new_stock - old_stock,
                    old_stock,
                    new_stock,
                    '手动调整库存'
                ))

        if 'min_stock_level' in data:
            update_fields.append("min_stock_level = %s")
            values.append(int(data['min_stock_level']))
        if 'max_stock_level' in data:
            update_fields.append("max_stock_level = %s")
            values.append(int(data['max_stock_level']))
        if 'warehouse_location' in data:
            update_fields.append("warehouse_location = %s")
            values.append(data['warehouse_location'])
        if 'status' in data:
            update_fields.append("status = %s")
            values.append(data['status'])

        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        if update_fields:
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s"
            values.append(product_id)
            cursor.execute(query, tuple(values))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': '产品更新成功'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """删除产品"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查产品是否存在
        cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': '产品不存在'}), 404

        # 删除产品（实际项目中可能需要软删除）
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': '产品删除成功'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 库存管理API ====================
@app.route('/api/inventory/alerts', methods=['GET'])
def get_stock_alerts():
    """获取库存预警"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 使用存储过程或直接查询
        cursor.execute("""
            SELECT 
                p.product_id,
                p.product_code,
                p.product_name,
                p.current_stock,
                p.min_stock_level,
                p.max_stock_level,
                CASE 
                    WHEN p.current_stock < p.min_stock_level THEN '库存不足'
                    WHEN p.current_stock > p.max_stock_level THEN '库存过剩'
                    ELSE '正常'
                END as alert_type,
                CASE 
                    WHEN p.current_stock < p.min_stock_level THEN p.min_stock_level - p.current_stock
                    WHEN p.current_stock > p.max_stock_level THEN p.current_stock - p.max_stock_level
                    ELSE 0
                END as alert_value
            FROM products p
            WHERE p.current_stock < p.min_stock_level OR p.current_stock > p.max_stock_level
            ORDER BY alert_type, ABS(p.current_stock - p.min_stock_level) DESC
        """)

        alerts = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(alerts)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/inventory/transactions', methods=['GET'])
def get_inventory_transactions():
    """获取库存变动记录"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        product_id = request.args.get('product_id')
        limit = int(request.args.get('limit', 50))

        query = """
            SELECT 
                it.*,
                p.product_name,
                p.product_code
            FROM inventory_transactions it
            JOIN products p ON it.product_id = p.product_id
            WHERE 1=1
        """
        params = []

        if product_id:
            query += " AND it.product_id = %s"
            params.append(product_id)

        query += " ORDER BY it.transaction_date DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
        transactions = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(transactions)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/inventory/adjust', methods=['POST'])
def adjust_inventory():
    """调整库存"""
    try:
        data = request.json

        if 'product_id' not in data or 'quantity' not in data:
            return jsonify({'error': '缺少必要参数'}), 400

        product_id = data['product_id']
        quantity = int(data['quantity'])
        notes = data.get('notes', '手动调整库存')

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 获取当前库存
        cursor.execute("SELECT current_stock FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': '产品不存在'}), 404

        old_stock = result[0]
        new_stock = quantity

        # 更新库存
        cursor.execute("UPDATE products SET current_stock = %s, updated_at = CURRENT_TIMESTAMP WHERE product_id = %s",
                       (new_stock, product_id))

        # 记录库存变动
        cursor.execute("""
            INSERT INTO inventory_transactions (
                product_id, transaction_type, quantity_change,
                quantity_before, quantity_after, notes
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            product_id,
            '库存调整',
            new_stock - old_stock,
            old_stock,
            new_stock,
            notes
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '库存调整成功',
            'product_id': product_id,
            'old_stock': old_stock,
            'new_stock': new_stock,
            'change': new_stock - old_stock
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 销售统计API ====================
@app.route('/api/statistics/sales', methods=['GET'])
def get_sales_statistics():
    """获取销售统计"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 月度销售统计（如果有销售数据）
        cursor.execute("""
            SELECT 
                DATE_FORMAT(order_date, '%Y-%m') as month,
                COUNT(*) as order_count,
                COALESCE(SUM(total_amount), 0) as total_amount,
                COALESCE(AVG(total_amount), 0) as avg_order_amount
            FROM sales_orders 
            WHERE status = '已完成'
            GROUP BY DATE_FORMAT(order_date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 12
        """)
        monthly_stats = cursor.fetchall()

        # 如果还没有销售数据，使用模拟数据
        if not monthly_stats:
            monthly_stats = [
                {'month': '2024-03', 'order_count': 0, 'total_amount': 0, 'avg_order_amount': 0},
                {'month': '2024-02', 'order_count': 0, 'total_amount': 0, 'avg_order_amount': 0},
                {'month': '2024-01', 'order_count': 0, 'total_amount': 0, 'avg_order_amount': 0}
            ]

        # 产品类别销售统计
        cursor.execute("""
            SELECT 
                p.material_type,
                COALESCE(SUM(sod.quantity), 0) as total_quantity,
                COALESCE(SUM(sod.total_price), 0) as total_amount,
                COALESCE(COUNT(DISTINCT so.order_id), 0) as order_count
            FROM products p
            LEFT JOIN sales_order_details sod ON p.product_id = sod.product_id
            LEFT JOIN sales_orders so ON sod.order_id = so.order_id AND so.status = '已完成'
            GROUP BY p.material_type
            ORDER BY total_amount DESC
        """)
        category_stats = cursor.fetchall()

        # 客户销售排名
        cursor.execute("""
            SELECT 
                c.customer_name,
                c.customer_type,
                COALESCE(COUNT(so.order_id), 0) as order_count,
                COALESCE(SUM(so.total_amount), 0) as total_amount
            FROM customers c
            LEFT JOIN sales_orders so ON c.customer_id = so.customer_id AND so.status = '已完成'
            GROUP BY c.customer_id
            ORDER BY total_amount DESC
            LIMIT 10
        """)
        customer_stats = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'monthly': monthly_stats,
            'by_category': category_stats,
            'by_customer': customer_stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 客户管理API ====================
@app.route('/api/customers', methods=['GET'])
def get_customers():
    """获取客户列表"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 支持分页和筛选
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        customer_type = request.args.get('customer_type', '')
        status = request.args.get('status', '')
        search = request.args.get('search', '')

        query = "SELECT * FROM customers WHERE 1=1"
        params = []

        if customer_type:
            query += " AND customer_type = %s"
            params.append(customer_type)
        if status:
            query += " AND status = %s"
            params.append(status)
        if search:
            query += " AND (customer_name LIKE %s OR customer_code LIKE %s OR contact_person LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

        # 获取总数
        count_query = query.replace("SELECT *", "SELECT COUNT(*) as total")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 获取分页数据
        query += " ORDER BY customer_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, params)
        customers = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'data': customers,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/customers', methods=['POST'])
def create_customer():
    """创建新客户"""
    try:
        data = request.json
        print("创建客户数据:", data)

        # 验证必要字段
        required_fields = ['customer_code', 'customer_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查客户编码是否重复
        cursor.execute("SELECT customer_id FROM customers WHERE customer_code = %s", (data['customer_code'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': '客户编码已存在'}), 400

        # 插入新客户
        query = """
            INSERT INTO customers (
                customer_code, customer_name, contact_person, phone,
                email, address, customer_type, credit_level, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['customer_code'],
            data['customer_name'],
            data.get('contact_person', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('address', ''),
            data.get('customer_type', '终端客户'),
            data.get('credit_level', '中'),
            data.get('status', '活跃')
        )

        cursor.execute(query, values)
        customer_id = cursor.lastrowid

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '客户创建成功',
            'customer_id': customer_id,
            'customer_code': data['customer_code']
        }), 201

    except Exception as e:
        print("创建客户错误:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """获取单个客户详情"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

        cursor.close()
        conn.close()

        if not customer:
            return jsonify({'error': '客户不存在'}), 404

        return jsonify(customer)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 供应商管理API ====================
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """获取供应商列表"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 支持分页和筛选
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        rating = request.args.get('rating', '')
        status = request.args.get('status', '')
        search = request.args.get('search', '')

        query = "SELECT * FROM suppliers WHERE 1=1"
        params = []

        if rating:
            query += " AND rating = %s"
            params.append(rating)
        if status:
            query += " AND status = %s"
            params.append(status)
        if search:
            query += " AND (supplier_name LIKE %s OR supplier_code LIKE %s OR contact_person LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

        # 获取总数
        count_query = query.replace("SELECT *", "SELECT COUNT(*) as total")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 获取分页数据
        query += " ORDER BY supplier_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, params)
        suppliers = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'data': suppliers,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/suppliers', methods=['POST'])
def create_supplier():
    """创建新供应商"""
    try:
        data = request.json
        print("创建供应商数据:", data)

        # 验证必要字段
        required_fields = ['supplier_code', 'supplier_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查供应商编码是否重复
        cursor.execute("SELECT supplier_id FROM suppliers WHERE supplier_code = %s", (data['supplier_code'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': '供应商编码已存在'}), 400

        # 插入新供应商
        query = """
            INSERT INTO suppliers (
                supplier_code, supplier_name, contact_person, phone,
                email, address, rating, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['supplier_code'],
            data['supplier_name'],
            data.get('contact_person', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('address', ''),
            data.get('rating', 'B'),
            data.get('status', '合作中')
        )

        cursor.execute(query, values)
        supplier_id = cursor.lastrowid

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '供应商创建成功',
            'supplier_id': supplier_id,
            'supplier_code': data['supplier_code']
        }), 201

    except Exception as e:
        print("创建供应商错误:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """获取单个供应商详情"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        supplier = cursor.fetchone()

        cursor.close()
        conn.close()

        if not supplier:
            return jsonify({'error': '供应商不存在'}), 404

        return jsonify(supplier)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 采购订单管理API ====================
@app.route('/api/purchase/orders', methods=['GET'])
def get_purchase_orders():
    """获取采购订单列表"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 支持分页和筛选
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        status = request.args.get('status', '')
        supplier_id = request.args.get('supplier_id', '')
        search = request.args.get('search', '')

        query = """
            SELECT po.*, s.supplier_name 
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.supplier_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND po.status = %s"
            params.append(status)
        if supplier_id:
            query += " AND po.supplier_id = %s"
            params.append(supplier_id)
        if search:
            query += " AND po.order_number LIKE %s"
            params.append(f'%{search}%')

        # 获取总数
        count_query = query.replace("SELECT po.*, s.supplier_name", "SELECT COUNT(*) as total")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 获取分页数据
        query += " ORDER BY po.order_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, params)
        orders = cursor.fetchall()

        # 获取每个订单的明细
        for order in orders:
            cursor.execute("""
                SELECT pod.*, p.product_code, p.product_name 
                FROM purchase_order_details pod
                JOIN products p ON pod.product_id = p.product_id
                WHERE pod.order_id = %s
            """, (order['order_id'],))
            order['items'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'data': orders,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/purchase/orders/pending', methods=['GET'])
def get_pending_purchase_orders():
    """获取待处理采购订单"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM purchase_orders 
            WHERE status IN ('待审核', '已批准', '已发货')
        """)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            'pending_count': result['count'] if result else 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/purchase/orders', methods=['POST'])
def create_purchase_order():
    """创建采购订单"""
    try:
        data = request.json
        print("创建采购订单数据:", data)

        # 验证必要字段
        required_fields = ['supplier_id', 'order_date', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400

        if not data['items'] or len(data['items']) == 0:
            return jsonify({'error': '采购订单必须包含至少一个项目'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 生成订单号
        order_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(random.randint(1000, 9999))}"

        # 插入采购订单
        query = """
            INSERT INTO purchase_orders (
                order_number, supplier_id, order_date, 
                expected_delivery_date, total_amount, status, 
                notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 计算订单总额
        total_amount = sum(item['quantity'] * item['unit_price'] for item in data['items'])

        values = (
            order_number,
            data['supplier_id'],
            data['order_date'],
            data.get('expected_delivery_date'),
            total_amount,
            data.get('status', '待审核'),
            data.get('notes', ''),
            data.get('created_by', 'admin')
        )

        cursor.execute(query, values)
        order_id = cursor.lastrowid

        # 插入采购订单明细
        for item in data['items']:
            cursor.execute("""
                INSERT INTO purchase_order_details (
                    order_id, product_id, quantity, unit_price
                ) VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item['product_id'],
                item['quantity'],
                item['unit_price']
            ))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '采购订单创建成功',
            'order_id': order_id,
            'order_number': order_number,
            'status': '待审核'
        }), 201

    except Exception as e:
        print("创建采购订单错误:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/purchase/orders/<int:order_id>', methods=['GET'])
def get_purchase_order(order_id):
    """获取单个采购订单详情"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 获取订单基本信息
        cursor.execute("""
            SELECT po.*, s.supplier_name, s.supplier_code 
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.supplier_id
            WHERE po.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({'error': '采购订单不存在'}), 404

        # 获取订单明细
        cursor.execute("""
            SELECT pod.*, p.product_code, p.product_name, p.specification
            FROM purchase_order_details pod
            JOIN products p ON pod.product_id = p.product_id
            WHERE pod.order_id = %s
        """, (order_id,))
        order['items'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(order)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/purchase/orders/<int:order_id>/approve', methods=['PUT'])
def approve_purchase_order(order_id):
    """审核通过采购订单"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查订单是否存在
        cursor.execute("SELECT status FROM purchase_orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': '采购订单不存在'}), 404

        current_status = result[0]
        if current_status != '待审核':
            cursor.close()
            conn.close()
            return jsonify({'error': f'订单当前状态为{current_status}，无法审核'}), 400

        # 更新订单状态
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = '已批准', updated_at = CURRENT_TIMESTAMP 
            WHERE order_id = %s
        """, (order_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '采购订单审核通过',
            'order_id': order_id,
            'status': '已批准'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/purchase/orders/<int:order_id>/cancel', methods=['PUT'])
def cancel_purchase_order(order_id):
    """取消采购订单"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查订单是否存在
        cursor.execute("SELECT status FROM purchase_orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': '采购订单不存在'}), 404

        current_status = result[0]
        if current_status in ['已完成', '已取消']:
            cursor.close()
            conn.close()
            return jsonify({'error': f'订单当前状态为{current_status}，无法取消'}), 400

        # 更新订单状态
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = '已取消', updated_at = CURRENT_TIMESTAMP 
            WHERE order_id = %s
        """, (order_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '采购订单已取消',
            'order_id': order_id,
            'status': '已取消'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 销售订单管理API ====================
@app.route('/api/sales/orders', methods=['GET'])
def get_sales_orders():
    """获取销售订单列表"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 支持分页和筛选
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        status = request.args.get('status', '')
        customer_id = request.args.get('customer_id', '')
        payment_status = request.args.get('payment_status', '')
        search = request.args.get('search', '')

        query = """
            SELECT so.*, c.customer_name 
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND so.status = %s"
            params.append(status)
        if customer_id:
            query += " AND so.customer_id = %s"
            params.append(customer_id)
        if payment_status:
            query += " AND so.payment_status = %s"
            params.append(payment_status)
        if search:
            query += " AND so.order_number LIKE %s"
            params.append(f'%{search}%')

        # 获取总数
        count_query = query.replace("SELECT so.*, c.customer_name", "SELECT COUNT(*) as total")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 获取分页数据
        query += " ORDER BY so.order_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, params)
        orders = cursor.fetchall()

        # 获取每个订单的明细
        for order in orders:
            cursor.execute("""
                SELECT sod.*, p.product_code, p.product_name 
                FROM sales_order_details sod
                JOIN products p ON sod.product_id = p.product_id
                WHERE sod.order_id = %s
            """, (order['order_id'],))
            order['items'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'data': orders,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sales/orders/pending', methods=['GET'])
def get_pending_sales_orders():
    """获取待处理销售订单"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM sales_orders 
            WHERE status IN ('待处理', '已确认', '发货中')
        """)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            'pending_count': result['count'] if result else 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sales/orders', methods=['POST'])
def create_sales_order():
    """创建销售订单"""
    try:
        data = request.json
        print("创建销售订单数据:", data)

        # 验证必要字段
        required_fields = ['customer_id', 'order_date', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400

        if not data['items'] or len(data['items']) == 0:
            return jsonify({'error': '销售订单必须包含至少一个项目'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 生成订单号
        order_number = f"SO-{datetime.now().strftime('%Y%m%d')}-{str(random.randint(1000, 9999))}"

        # 插入销售订单
        query = """
            INSERT INTO sales_orders (
                order_number, customer_id, order_date, 
                delivery_date, total_amount, status, 
                payment_status, payment_method, notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 计算订单总额
        total_amount = sum(item['quantity'] * item['unit_price'] for item in data['items'])

        values = (
            order_number,
            data['customer_id'],
            data['order_date'],
            data.get('delivery_date'),
            total_amount,
            data.get('status', '待处理'),
            data.get('payment_status', '未支付'),
            data.get('payment_method', '现金'),
            data.get('notes', ''),
            data.get('created_by', 'admin')
        )

        cursor.execute(query, values)
        order_id = cursor.lastrowid

        # 插入销售订单明细
        for item in data['items']:
            cursor.execute("""
                INSERT INTO sales_order_details (
                    order_id, product_id, quantity, unit_price
                ) VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item['product_id'],
                item['quantity'],
                item['unit_price']
            ))

            # 更新产品库存（检查库存是否充足）
            cursor.execute("SELECT current_stock FROM products WHERE product_id = %s", (item['product_id'],))
            current_stock = cursor.fetchone()[0]

            if current_stock < item['quantity']:
                conn.rollback()
                cursor.close()
                conn.close()
                return jsonify({'error': f'产品ID {item["product_id"]} 库存不足'}), 400

            # 扣减库存
            cursor.execute("""
                UPDATE products 
                SET current_stock = current_stock - %s, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE product_id = %s
            """, (item['quantity'], item['product_id']))

            # 记录库存变动
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    product_id, transaction_type, quantity_change,
                    quantity_before, quantity_after, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                item['product_id'],
                '销售出库',
                -item['quantity'],
                current_stock,
                current_stock - item['quantity'],
                f'销售订单: {order_number}'
            ))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '销售订单创建成功',
            'order_id': order_id,
            'order_number': order_number,
            'status': '待处理'
        }), 201

    except Exception as e:
        print("创建销售订单错误:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/sales/orders/<int:order_id>', methods=['GET'])
def get_sales_order(order_id):
    """获取单个销售订单详情"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)

        # 获取订单基本信息
        cursor.execute("""
            SELECT so.*, c.customer_name, c.customer_code 
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.customer_id
            WHERE so.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({'error': '销售订单不存在'}), 404

        # 获取订单明细
        cursor.execute("""
            SELECT sod.*, p.product_code, p.product_name, p.specification
            FROM sales_order_details sod
            JOIN products p ON sod.product_id = p.product_id
            WHERE sod.order_id = %s
        """, (order_id,))
        order['items'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(order)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sales/orders/<int:order_id>/confirm', methods=['PUT'])
def confirm_sales_order(order_id):
    """确认销售订单"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查订单是否存在
        cursor.execute("SELECT status FROM sales_orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': '销售订单不存在'}), 404

        current_status = result[0]
        if current_status != '待处理':
            cursor.close()
            conn.close()
            return jsonify({'error': f'订单当前状态为{current_status}，无法确认'}), 400

        # 更新订单状态
        cursor.execute("""
            UPDATE sales_orders 
            SET status = '已确认', updated_at = CURRENT_TIMESTAMP 
            WHERE order_id = %s
        """, (order_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '销售订单已确认',
            'order_id': order_id,
            'status': '已确认'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sales/orders/<int:order_id>/cancel', methods=['PUT'])
def cancel_sales_order(order_id):
    """取消销售订单"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor()

        # 检查订单是否存在
        cursor.execute("SELECT status FROM sales_orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': '销售订单不存在'}), 404

        current_status = result[0]
        if current_status in ['已完成', '已取消']:
            cursor.close()
            conn.close()
            return jsonify({'error': f'订单当前状态为{current_status}，无法取消'}), 400

        # 恢复库存
        cursor.execute("""
            SELECT sod.product_id, sod.quantity, p.current_stock
            FROM sales_order_details sod
            JOIN products p ON sod.product_id = p.product_id
            WHERE sod.order_id = %s
        """, (order_id,))
        order_items = cursor.fetchall()

        for item in order_items:
            product_id = item[0]
            quantity = item[1]
            current_stock = item[2]

            # 恢复库存
            cursor.execute("""
                UPDATE products 
                SET current_stock = current_stock + %s, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE product_id = %s
            """, (quantity, product_id))

            # 记录库存变动
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    product_id, transaction_type, quantity_change,
                    quantity_before, quantity_after, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                product_id,
                '库存调整',
                quantity,
                current_stock,
                current_stock + quantity,
                f'销售订单取消恢复库存: {order_id}'
            ))

        # 更新订单状态
        cursor.execute("""
            UPDATE sales_orders 
            SET status = '已取消', updated_at = CURRENT_TIMESTAMP 
            WHERE order_id = %s
        """, (order_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '销售订单已取消',
            'order_id': order_id,
            'status': '已取消'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 产品类别API ====================
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取产品类别列表"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product_categories ORDER BY category_id")
        categories = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(categories)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 运行应用 ====================
if __name__ == '__main__':
    print("工厂氟胶垫片库存管理系统")
    print("服务地址: http://127.0.0.1:5000")
    print("数据库: factory_inventory_db")
    print("主页: http://127.0.0.1:5000/")
    print("产品API: http://127.0.0.1:5000/api/products")
    print("⚠库存预警: http://127.0.0.1:5000/api/inventory/alerts")

    # 测试数据库连接
    conn = get_db_connection()
    if conn:
        print("数据库连接成功")
        conn.close()
    else:
        print("数据库连接失败，请检查配置")
        print(f"配置: {db_config}")

    app.run(debug=True, port=5000, host='127.0.0.1')