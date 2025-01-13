import torch
from diffusers import StableDiffusionPipeline
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import base64
import io
from functools import lru_cache

app = Flask(__name__)
CORS(app)

# モデルの事前読み込みと最適化
def load_optimized_model():
    model_id = "runwayml/stable-diffusion-v1-5"
    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            variant="fp16",
            safety_checker=None,
            requires_safety_checker=False
        )
        
        # GPU最適化
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
            pipe.enable_attention_slicing()
            try:
                pipe.enable_xformers_memory_efficient_attention()
            except:
                print("xformersが利用できません。通常の最適化を適用します。")
        
        return pipe
    except Exception as e:
        print(f"モデル読み込みエラー: {e}")
        return None

# グローバルモデル
global_pipe = load_optimized_model()

# キャッシュ付き画像生成
@lru_cache(maxsize=10)
def generate_cached_image(prompt):
    if global_pipe is None:
        raise ValueError("モデルが読み込まれていません")
    
    try:
        # 高速化パラメータ
        image = global_pipe(
            prompt, 
            num_inference_steps=20,  # デフォルトより少ない手順
            guidance_scale=7.5,
            height=512,
            width=512
        ).images[0]
        
        # 画像をBase64に変換
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"画像生成エラー: {e}")
        return None

@app.route('/generate', methods=['POST'])
def generate_image_endpoint():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'プロンプトが空です'}), 400
    
    try:
        # キャッシュ付き画像生成
        image_base64 = generate_cached_image(prompt)
        
        if image_base64:
            return jsonify({'image': image_base64})
        else:
            return jsonify({'error': '画像生成に失敗しました'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)