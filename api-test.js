/**
 * 泰迪杯项目 - API配置测试脚本
 * 功能: 测试api-config.js的配置加载功能
 */

// 等待API配置加载完成
document.addEventListener('api-config-loaded', function(e) {
    console.log('API配置加载完成，当前配置:', e.detail);
    
    // 验证端口是否为53085
    if (e.detail.port === 53085) {
        console.log('✅ 端口配置正确: 53085');
    } else {
        console.error('❌ 端口配置错误:', e.detail.port);
    }
    
    // 验证baseUrl是否包含53085
    if (e.detail.baseUrl.includes(':53085/api')) {
        console.log('✅ API基础URL配置正确:', e.detail.baseUrl);
    } else {
        console.error('❌ API基础URL配置错误:', e.detail.baseUrl);
    }
    
    // 测试getApiUrl函数
    const testEndpoint = '/qa/answer';
    const apiUrl = getApiUrl(testEndpoint);
    console.log('测试endpoint:', testEndpoint);
    console.log('生成的API URL:', apiUrl);
    
    if (apiUrl === `${e.detail.baseUrl}${testEndpoint}`) {
        console.log('✅ getApiUrl函数工作正常');
    } else {
        console.error('❌ getApiUrl函数工作异常');
    }
    
    // 显示测试结果到页面
    const resultContainer = document.getElementById('api-test-result');
    if (resultContainer) {
        resultContainer.innerHTML = `
            <div style="padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-top: 20px;">
                <h3>API配置测试结果</h3>
                <p><strong>主机:</strong> ${e.detail.host}</p>
                <p><strong>端口:</strong> ${e.detail.port}</p>
                <p><strong>基础URL:</strong> ${e.detail.baseUrl}</p>
                <p><strong>测试endpoint:</strong> ${testEndpoint}</p>
                <p><strong>生成的API URL:</strong> ${apiUrl}</p>
                <p style="color: ${e.detail.port === 53085 ? 'green' : 'red'}">
                    ${e.detail.port === 53085 ? '✅ 端口配置正确' : '❌ 端口配置错误'}
                </p>
            </div>
        `;
    }
});

// 页面加载时输出默认配置
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，当前API默认配置:', window.API_CONFIG);
}); 