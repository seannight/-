/**
 * 泰迪杯项目 - 前端实例API配置
 * 功能: 从配置文件读取API端口，并配置API URL
 */

// 默认API配置
window.API_CONFIG = {
    host: '127.0.0.1',
    port: 53085,
    baseUrl: 'http://127.0.0.1:53085/api'
};

// 从配置文件加载配置
function loadApiConfig() {
    fetch('/teddy_config.txt')
        .then(response => {
            if (!response.ok) {
                console.warn('无法加载API配置文件，使用默认配置');
                return null;
            }
            return response.text();
        })
        .then(text => {
            if (!text) return;
            
            // 解析配置文件
            const portMatch = text.match(/API_PORT=(\d+)/);
            const hostMatch = text.match(/API_HOST=([\w\.]+)/);
            
            if (portMatch && portMatch[1]) {
                window.API_CONFIG.port = parseInt(portMatch[1]);
            }
            
            if (hostMatch && hostMatch[1]) {
                window.API_CONFIG.host = hostMatch[1];
            }
            
            // 更新基础URL
            window.API_CONFIG.baseUrl = `http://${window.API_CONFIG.host}:${window.API_CONFIG.port}/api`;
            
            console.log('API配置已加载:', window.API_CONFIG);
            
            // 触发配置加载完成事件
            document.dispatchEvent(new CustomEvent('api-config-loaded', { detail: window.API_CONFIG }));
        })
        .catch(error => {
            console.error('加载API配置出错:', error);
        });
}

// 获取API URL
function getApiUrl(endpoint) {
    return `${window.API_CONFIG.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
}

// 页面加载时自动加载配置
document.addEventListener('DOMContentLoaded', loadApiConfig);

// 导出API函数供其他JS文件使用
window.getApiUrl = getApiUrl; 