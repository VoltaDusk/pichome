// PicHome JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 自动隐藏 flash 消息
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-20px) scale(0.95)';
            setTimeout(() => msg.remove(), 300);
        }, 4000);
    });

    // 图片加载错误处理
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Crect fill=%22%23f1f5f9%22 width=%22100%22 height=%22100%22/%3E%3Ctext x=%2250%22 y=%2250%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%2394a3b8%22 font-size=%2214%22%3E图片加载失败%3C/text%3E%3C/svg%3E';
        });
        
        // 添加图片加载动画
        if (img.complete) {
            img.style.opacity = '1';
        } else {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.5s ease';
            img.addEventListener('load', function() {
                this.style.opacity = '1';
            });
        }
    });

    // 添加卡片入场动画
    const cards = document.querySelectorAll('.gallery-item, .stat-card, .auth-card, .upload-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// 复制到剪贴板（接收按钮元素）
function copyToClipboard(btn) {
    // 找到相邻的 code 元素
    const parent = btn.parentElement;
    const codeEl = parent.querySelector('code');
    const text = codeEl ? codeEl.textContent.trim() : '';
    
    if (!text) return;
    
    // 添加点击反馈
    btn.style.transform = 'scale(0.95)';
    setTimeout(() => btn.style.transform = '', 150);
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            btn.textContent = '已复制!';
            btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            setTimeout(() => {
                btn.textContent = '复制';
                btn.style.background = '';
            }, 2000);
        }).catch(() => {
            btn.textContent = '失败';
            btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            setTimeout(() => {
                btn.textContent = '复制';
                btn.style.background = '';
            }, 2000);
        });
    } else {
        // 兼容旧浏览器
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        
        btn.textContent = '已复制!';
        btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        setTimeout(() => {
            btn.textContent = '复制';
            btn.style.background = '';
        }, 2000);
    }
}