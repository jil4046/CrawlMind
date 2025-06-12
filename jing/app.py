import streamlit as st
import subprocess
import os
import sys

st.set_page_config(layout="wide")
st.title("🔬 Selenium 环境诊断工具")
st.write("本应用用于诊断 Streamlit Cloud 环境中 Selenium 运行失败的根本原因。")
st.markdown("---")

# --- 1. 检查 Python 和库的版本 ---
st.header("1. 环境基本信息")
st.write(f"**Python 版本:** `{sys.version}`")
try:
    import selenium
    st.write(f"**Selenium 版本:** `{selenium.__version__}`")
except ImportError:
    st.error("诊断失败：环境中未安装 `selenium` 库。")

# --- 这里是修正的部分 ---
try:
    import chromedriver_py
    # 我们不再尝试获取版本号，只确认库能被导入
    st.success("诊断信息：`chromedriver-py` 库已成功导入。")
except ImportError:
    st.error("诊断失败：环境中未安装 `chromedriver-py` 库。")

st.markdown("---")


# --- 2. 检查 packages.txt 安装的 Chrome 浏览器 ---
st.header("2. 检查 Chrome 浏览器")
st.write("通过 `packages.txt` 安装的 `google-chrome-stable` 是否存在？")
chrome_path = "/usr/bin/google-chrome-stable"
if os.path.exists(chrome_path):
    st.success(f"成功：在 `{chrome_path}` 路径下找到了 Chrome 浏览器。")
    try:
        result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True, check=True)
        st.write(f"**浏览器版本信息:** `{result.stdout.strip()}`")
    except Exception as e:
        st.error(f"尝试获取浏览器版本时出错: {e}")
else:
    st.error(f"失败：在 `{chrome_path}` 路径下**未找到** Chrome 浏览器。请检查 `packages.txt` 文件是否正确。")

st.markdown("---")


# --- 3. 检查 chromedriver-py 安装的驱动 ---
st.header("3. 检查 ChromeDriver 驱动程序")
st.write("通过 `requirements.txt` 安装的 `chromedriver-py` 是否能提供驱动路径？")
try:
    import chromedriver_py
    driver_path = chromedriver_py.binary_path
    st.success(f"成功：`chromedriver-py` 报告的驱动路径是：")
    st.code(driver_path, language='bash')

    st.write("现在检查该路径的文件是否存在及其权限：")
    if os.path.exists(driver_path):
        st.success("文件存在！正在检查权限...")
        result = subprocess.run(['ls', '-l', driver_path], capture_output=True, text=True, check=True)
        st.write("文件权限信息:")
        st.code(result.stdout.strip(), language='bash')
        if '-rwxr-xr-x' in result.stdout:
            st.success("诊断成功：驱动文件具有可执行权限。")
        else:
            st.error("诊断失败：驱动文件**不具有**可执行权限！")
    else:
        st.error(f"诊断失败：`chromedriver-py` 报告的路径 `{driver_path}` 下**没有**找到驱动文件！")

except ImportError:
    st.error("诊断失败：无法导入 `chromedriver-py`。请检查 `requirements.txt`。")
except Exception as e:
    st.error(f"在检查驱动程序时发生未知错误: {e}")

st.markdown("---")

# --- 4. 最终测试 ---
st.header("4. 最终初始化测试")
st.write("我们将使用上述诊断出的信息，尝试直接初始化 Selenium。")

if st.button("开始最终测试"):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    import chromedriver_py

    st.info("正在尝试初始化 WebDriver...")
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_graphical_env = False
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        driver_path = chromedriver_py.binary_path
        service = ChromeService(executable_path=driver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        
        st.success("✅✅✅ 恭喜！Selenium WebDriver 成功初始化！✅✅✅")
        st.balloons()
        
    except Exception as e:
        st.error("❌❌❌ 在最终测试中，Selenium 初始化再次失败。❌❌❌")
        st.exception(e) 
    finally:
        if driver:
            driver.quit()
        st.info("测试结束。")