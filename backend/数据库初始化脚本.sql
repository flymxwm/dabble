-- 创建数据库
CREATE DATABASE IF NOT EXISTS archive_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE archive_system;

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) UNIQUE NOT NULL COMMENT '角色名称',
  description VARCHAR(255) COMMENT '角色描述',
  permissions TEXT COMMENT '权限JSON字符串',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认角色
INSERT INTO roles (name, description, permissions) VALUES 
('管理员', '系统管理员，拥有所有权限', '{}'),
('普通用户', '只能查看和管理自己的档案', '{"view_own": true, "manage_own": true}');

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(128) NOT NULL,
  role_id INT NOT NULL COMMENT '1-管理员,2-普通用户',
  real_name VARCHAR(50) COMMENT '真实姓名',
  department VARCHAR(100) COMMENT '部门',
  phone VARCHAR(20) COMMENT '联系电话',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME,
  FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- 插入默认管理员用户(密码:admin123)
INSERT INTO users (username, password, role_id, real_name) VALUES 
('admin', 'pbkdf2:sha256:150000$abc123$def456', 1, '系统管理员');

-- 案卷表
CREATE TABLE IF NOT EXISTS archives (
  id INT PRIMARY KEY AUTO_INCREMENT,
  archive_no VARCHAR(30) UNIQUE NOT NULL COMMENT '案卷编号',
  title VARCHAR(255) NOT NULL,
  category_id INT COMMENT '档案类别',
  warehouse_id INT COMMENT '存放库房',
  storage_position VARCHAR(50) COMMENT '存放位置',
  security_level INT DEFAULT 1 COMMENT '1-公开,2-内部,3-机密',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME ON UPDATE CURRENT_TIMESTAMP
);

-- 库房表
CREATE TABLE IF NOT EXISTS warehouses (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL COMMENT '库房名称',
  location VARCHAR(255) COMMENT '库房位置',
  capacity INT COMMENT '容量(档案盒数)',
  manager_id INT COMMENT '管理员ID'
);

-- 借阅记录表
CREATE TABLE IF NOT EXISTS borrow_records (
  id INT PRIMARY KEY AUTO_INCREMENT,
  archive_id INT NOT NULL,
  user_id INT NOT NULL,
  borrow_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  due_date DATETIME NOT NULL,
  return_date DATETIME NULL,
  status INT DEFAULT 0 COMMENT '0-借阅中,1-已归还,2-超期'
);