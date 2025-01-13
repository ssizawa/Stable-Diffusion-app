document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt');
    const generateBtn = document.getElementById('generate-btn');
    const generatedImage = document.getElementById('generated-image');
    const loadingIndicator = document.getElementById('loading');

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        
        if (!prompt) {
            alert('プロンプトを入力してください');
            return;
        }

        // Show loading
        loadingIndicator.classList.remove('hidden');
        generatedImage.src = '';

        try {
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });

            const data = await response.json();

            if (data.image) {
                generatedImage.src = `data:image/png;base64,${data.image}`;
            } else if (data.error) {
                alert('画像生成中にエラーが発生しました: ' + data.error);
            }
        } catch (error) {
            console.error('エラー:', error);
            alert('通信エラーが発生しました');
        } finally {
            // Hide loading
            loadingIndicator.classList.add('hidden');
        }
    });
});
