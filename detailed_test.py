import urllib.request
import urllib.error
import socket
import time

def check_port(host, port):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_detailed():
    print("="*60)
    print("冰刀系统详细测试报告")
    print("="*60)
    
    # 检查端口
    print("端口检查:")
    backend_port = check_port('localhost', 8000)
    frontend_port = check_port('localhost', 5173)
    alt_frontend_port = check_port('localhost', 3000)
    
    print(f"  后端端口 8000: {'开放' if backend_port else '关闭'}")
    print(f"  前端端口 5173: {'开放' if frontend_port else '关闭'}")
    print(f"  前端端口 3000: {'开放' if alt_frontend_port else '关闭'}")
    
    # HTTP测试
    print("\nHTTP连接测试:")
    
    # 测试后端
    if backend_port:
        try:
            resp = urllib.request.urlopen('http://localhost:8000/', timeout=3)
            print(f"  ✓ 后端根路径: HTTP {resp.status}")
        except Exception as e:
            print(f"  ✗ 后端根路径: {e}")
        
        try:
            resp = urllib.request.urlopen('http://localhost:8000/admin/', timeout=3)
            print(f"  ✓ 后端管理页面: HTTP {resp.status}")
        except Exception as e:
            print(f"  ✗ 后端管理页面: {e}")
    else:
        print("  ✗ 后端服务器未启动")
    
    # 测试前端
    if frontend_port:
        try:
            resp = urllib.request.urlopen('http://localhost:5173/', timeout=3)
            print(f"  ✓ 前端应用: HTTP {resp.status}")
        except Exception as e:
            print(f"  ✗ 前端应用: {e}")
    elif alt_frontend_port:
        try:
            resp = urllib.request.urlopen('http://localhost:3000/', timeout=3)
            print(f"  ✓ 前端应用(3000): HTTP {resp.status}")
        except Exception as e:
            print(f"  ✗ 前端应用(3000): {e}")
    else:
        print("  ✗ 前端服务器未启动")
    
    print("\n" + "="*60)
    print("启动建议:")
    if not backend_port:
        print("  后端: cd iceskate_system && python manage.py runserver 8000")
    if not frontend_port and not alt_frontend_port:
        print("  前端: cd frontend && npm run dev")
    
    if backend_port and (frontend_port or alt_frontend_port):
        print("  🎉 前后端服务器运行正常!")
        print("  访问地址:")
        if frontend_port:
            print("    前端: http://localhost:5173/")
        if alt_frontend_port:
            print("    前端: http://localhost:3000/")
        if backend_port:
            print("    后端: http://localhost:8000/")
            print("    管理: http://localhost:8000/admin/")
    
    print("="*60)

if __name__ == '__main__':
    test_detailed() 