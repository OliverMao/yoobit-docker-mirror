document.addEventListener('DOMContentLoaded', function() {
    const updateForm = document.getElementById('updateForm');
    const logContainer = document.getElementById('logContainer');

    function addLogEntry(message, type = 'info') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    updateForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const imageName = document.getElementById('imageName').value;
        const tag = document.getElementById('tag').value;

        if (!imageName) {
            Swal.fire({
                icon: 'error',
                title: '错误',
                text: '请输入镜像名称'
            });
            return;
        }

        try {
            addLogEntry(`开始更新镜像: ${imageName}:${tag}`);
            
            const response = await fetch('/update_and_push', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_name: imageName,
                    tag: tag
                })
            });

            const data = await response.json();

            if (response.ok) {
                addLogEntry(`镜像 ${imageName}:${tag} 更新成功`, 'success');
                Swal.fire({
                    icon: 'success',
                    title: '成功',
                    text: '镜像更新并推送成功！'
                });
            } else {
                throw new Error(data.error || '更新失败');
            }
        } catch (error) {
            addLogEntry(`错误: ${error.message}`, 'error');
            Swal.fire({
                icon: 'error',
                title: '错误',
                text: error.message
            });
        }
    });
});
