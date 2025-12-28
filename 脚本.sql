
-- 工厂氟胶垫片库存交易系统数据库脚本
-- 数据库名称: factory

-- 创建数据库
CREATE DATABASE IF NOT EXISTS factory;
USE factory;

--  1.产品类别表
CREATE TABLE product_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 产品表
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(20) UNIQUE NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category_id INT,
    specification VARCHAR(200),
    material_type ENUM('氟胶', '垫片', '其他') NOT NULL,
    unit VARCHAR(20) DEFAULT '个',
    unit_price DECIMAL(10, 2) NOT NULL,
    min_stock_level INT DEFAULT 10,
    max_stock_level INT DEFAULT 1000,
    current_stock INT DEFAULT 0,
    warehouse_location VARCHAR(100),
    status ENUM('正常', '停用') DEFAULT '正常',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id) ON DELETE SET NULL
);

-- 3. 供应商表
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_code VARCHAR(20) UNIQUE NOT NULL,
    supplier_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(200),
    rating ENUM('A', 'B', 'C', 'D') DEFAULT 'B',
    status ENUM('合作中', '已终止') DEFAULT '合作中',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 客户表
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(200),
    customer_type ENUM('代理商', '终端客户', '经销商') DEFAULT '终端客户',
    credit_level ENUM('高', '中', '低') DEFAULT '中',
    status ENUM('活跃', '休眠', '终止') DEFAULT '活跃',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 采购订单表
CREATE TABLE purchase_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(30) UNIQUE NOT NULL,
    supplier_id INT,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    total_amount DECIMAL(12, 2) DEFAULT 0,
    status ENUM('待审核', '已批准', '已发货', '已完成', '已取消') DEFAULT '待审核',
    notes TEXT,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
);

-- 6. 采购订单明细表
CREATE TABLE purchase_order_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    received_quantity INT DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES purchase_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 7. 销售订单表
CREATE TABLE sales_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(30) UNIQUE NOT NULL,
    customer_id INT,
    order_date DATE NOT NULL,
    delivery_date DATE,
    total_amount DECIMAL(12, 2) DEFAULT 0,
    status ENUM('待处理', '已确认', '发货中', '已完成', '已取消') DEFAULT '待处理',
    payment_status ENUM('未支付', '部分支付', '已支付') DEFAULT '未支付',
    notes TEXT,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
);

-- 8. 销售订单明细表
CREATE TABLE sales_order_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    shipped_quantity INT DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES sales_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 9. 库存变动记录表
CREATE TABLE inventory_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    transaction_type ENUM('采购入库', '销售出库', '库存调整', '盘点') NOT NULL,
    reference_id INT COMMENT '关联的订单ID',
    reference_type ENUM('采购订单', '销售订单', '调整单') COMMENT '关联单据类型',
    quantity_change INT NOT NULL COMMENT '正数表示入库，负数表示出库',
    quantity_before INT NOT NULL,
    quantity_after INT NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(200),
    created_by VARCHAR(50),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 10. 用户表（用于系统登录）
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('管理员', '采购员', '销售员', '库存管理员') DEFAULT '库存管理员',
    email VARCHAR(100),
    phone VARCHAR(20),
    status ENUM('活跃', '停用') DEFAULT '活跃',
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 插入示例数据
-- 插入产品类别
INSERT INTO product_categories (category_name, description) VALUES
('密封件', '各种密封用氟胶制品'),
('垫片', '工业用垫片系列'),
('O型圈', '标准及非标O型圈'),
('其他配件', '其他相关配件');

-- 插入供应商
INSERT INTO suppliers (supplier_code, supplier_name, contact_person, phone, email, address, rating) VALUES
('SUP001', '华东氟胶有限公司', '张经理', '13800138000', 'sales@eastfluor.com', '上海市浦东新区', 'A'),
('SUP002', '华南密封件厂', '李主管', '13900139000', 'info@sealing.com', '广东省深圳市', 'B'),
('SUP003', '北方垫片制造', '王总', '13600136000', 'north@gasket.com', '北京市朝阳区', 'A');

-- 插入客户
INSERT INTO customers (customer_code, customer_name, contact_person, phone, email, address, customer_type) VALUES
('CUST001', '华润机械制造', '陈工', '13700137000', 'chen@huarun.com', '江苏省苏州市', '终端客户'),
('CUST002', '东方化工集团', '刘经理', '13500135000', 'liu@eastchem.com', '浙江省杭州市', '终端客户'),
('CUST003', '永信贸易公司', '赵总', '13300133000', 'zhao@yongxin.com', '广东省广州市', '代理商');

-- 插入产品
INSERT INTO products (product_code, product_name, category_id, specification, material_type, unit, unit_price, min_stock_level, max_stock_level, current_stock, warehouse_location) VALUES
('P001', '氟胶O型圈-10mm', 3, '内径10mm,截面2mm,耐高温250°C', '氟胶', '个', 5.50, 100, 1000, 500, 'A区-01架'),
('P002', '氟胶O型圈-15mm', 3, '内径15mm,截面2.5mm,耐油', '氟胶', '个', 6.80, 80, 800, 320, 'A区-02架'),
('P003', '金属缠绕垫片', 2, 'DN50,304不锈钢+石墨', '垫片', '片', 25.00, 50, 500, 150, 'B区-01架'),
('P004', '石棉垫片', 2, '3mm厚,耐压10MPa', '垫片', '片', 8.50, 200, 2000, 850, 'B区-03架'),
('P005', '氟胶平垫片', 1, 'Φ30×Φ15×2mm,耐酸碱', '氟胶', '个', 3.20, 300, 3000, 1200, 'C区-01架');

-- 插入用户
INSERT INTO users (username, password_hash, full_name, role, email) VALUES
('admin', '$2y$10$YourHashedPasswordHere', '系统管理员', '管理员', 'admin@factory.com'),
('purchase1', '$2y$10$YourHashedPasswordHere', '采购员张三', '采购员', 'purchase@factory.com'),
('sales1', '$2y$10$YourHashedPasswordHere', '销售员李四', '销售员', 'sales@factory.com');

-- 创建索引以提高查询性能


CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_material ON products(material_type);
CREATE INDEX idx_purchase_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_status ON purchase_orders(status);
CREATE INDEX idx_sales_customer ON sales_orders(customer_id);
CREATE INDEX idx_sales_status ON sales_orders(status);
CREATE INDEX idx_transactions_product ON inventory_transactions(product_id);
CREATE INDEX idx_transactions_date ON inventory_transactions(transaction_date);


-- 创建触发器：自动更新库存


DELIMITER //

-- 触发器：采购订单明细插入时更新库存
CREATE TRIGGER after_purchase_detail_insert
AFTER INSERT ON purchase_order_details
FOR EACH ROW
BEGIN
    -- 更新产品库存
    UPDATE products 
    SET current_stock = current_stock + NEW.quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = NEW.product_id;
    
    -- 记录库存变动
    INSERT INTO inventory_transactions (
        product_id, transaction_type, reference_id, reference_type,
        quantity_change, quantity_before, quantity_after, notes, created_by
    )
    SELECT 
        NEW.product_id,
        '采购入库',
        NEW.order_id,
        '采购订单',
        NEW.quantity,
        p.current_stock,
        p.current_stock + NEW.quantity,
        CONCAT('采购订单: ', po.order_number),
        po.created_by
    FROM products p
    JOIN purchase_orders po ON po.order_id = NEW.order_id
    WHERE p.product_id = NEW.product_id;
END//

-- 触发器：销售订单明细插入时更新库存
CREATE TRIGGER after_sale_detail_insert
AFTER INSERT ON sales_order_details
FOR EACH ROW
BEGIN
    -- 检查库存是否充足
    DECLARE current_stock INT;
    SELECT current_stock INTO current_stock FROM products WHERE product_id = NEW.product_id;
    
    IF current_stock >= NEW.quantity THEN
        -- 更新产品库存
        UPDATE products 
        SET current_stock = current_stock - NEW.quantity,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = NEW.product_id;
        
        -- 记录库存变动
        INSERT INTO inventory_transactions (
            product_id, transaction_type, reference_id, reference_type,
            quantity_change, quantity_before, quantity_after, notes, created_by
        )
        SELECT 
            NEW.product_id,
            '销售出库',
            NEW.order_id,
            '销售订单',
            -NEW.quantity,
            p.current_stock,
            p.current_stock - NEW.quantity,
            CONCAT('销售订单: ', so.order_number),
            so.created_by
        FROM products p
        JOIN sales_orders so ON so.order_id = NEW.order_id
        WHERE p.product_id = NEW.product_id;
    ELSE
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '库存不足，无法完成销售';
    END IF;
END//

DELIMITER ;


-- 创建存储过程：获取库存预警


DELIMITER //

CREATE PROCEDURE GetStockAlerts()
BEGIN
    SELECT 
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
    ORDER BY alert_type, ABS(p.current_stock - p.min_stock_level) DESC;
END//

DELIMITER ;


-- 创建视图：销售统计


CREATE VIEW sales_summary AS
SELECT 
    DATE_FORMAT(so.order_date, '%Y-%m') as month,
    p.material_type,
    p.category_id,
    c.category_name,
    COUNT(DISTINCT so.order_id) as order_count,
    SUM(sod.quantity) as total_quantity,
    SUM(sod.total_price) as total_amount,
    AVG(sod.unit_price) as avg_price
FROM sales_orders so
JOIN sales_order_details sod ON so.order_id = sod.order_id
JOIN products p ON sod.product_id = p.product_id
JOIN product_categories c ON p.category_id = c.category_id
WHERE so.status = '已完成'
GROUP BY DATE_FORMAT(so.order_date, '%Y-%m'), p.material_type, p.category_id; 
