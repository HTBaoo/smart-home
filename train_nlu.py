# import json
# import joblib
# import os
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# from sklearn.svm import SVC
# from sklearn.pipeline import make_pipeline

# # Cấu hình đường dẫn (phải khớp với config/settings.py của bạn)
# DATA_PATH = "data/nlu_data.json"
# MODEL_PATH = "models/nlu_model.pkl"
# VECTORIZER_PATH = "models/nlu_vectorizer.pkl"

# # Tạo thư mục nếu chưa có
# os.makedirs("models", exist_ok=True)

# def train_model():
#     print("🔄 Đang tải dữ liệu huấn luyện...")
    
#     # 1. Đọc dữ liệu
#     with open(DATA_PATH, "r", encoding="utf-8") as f:
#         dataset = json.load(f)

#     texts = [item["text"] for item in dataset]
#     labels = [item["intent"] for item in dataset]

#     print(f"📊 Tổng số mẫu câu: {len(texts)}")
#     print("⚙️  Đang training AI...")

#     # 2. Xử lý ngôn ngữ (Vectorizer)
#     # TfidfVectorizer giúp máy hiểu từ quan trọng (ví dụ: 'bật' quan trọng hơn 'đi')
#     vectorizer = TfidfVectorizer(ngram_range=(1, 2)) # Học cả từ đơn và cụm 2 từ
#     X = vectorizer.fit_transform(texts)

#     # 3. Chọn thuật toán (SVC là tốt nhất cho dữ liệu ít)
#     # probability=True để có thể tính % độ tin cậy
#     classifier = SVC(kernel='linear', probability=True)
#     classifier.fit(X, labels)

#     # 4. Lưu model ra file
#     joblib.dump(classifier, MODEL_PATH)
#     joblib.dump(vectorizer, VECTORIZER_PATH)

#     print("✅ Huấn luyện xong! Đã lưu model vào thư mục 'models/'.")
#     print("   Bây giờ bạn có thể chạy lại main.py để thử nghiệm.")

#     # Test thử luôn
#     test_sentence = "ánh sáng"
#     vec = vectorizer.transform([test_sentence])
#     pred = classifier.predict(vec)[0]
#     print(f"\n🧪 Test nhanh: '{test_sentence}' -> Intent: {pred}")

# if __name__ == "__main__":
#     train_model()
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

# ===========================
# 1) Load dataset
# ===========================
df = pd.read_csv("nlu_dataset.csv")

# ===========================
# 2) Train TFIDF vectorizer
# ===========================
vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
X = vectorizer.fit_transform(df["text"])
y = df["intent"]

# ===========================
# 3) Train model
# ===========================
model = LogisticRegression(max_iter=300)
model.fit(X, y)

# ===========================
# 4) Tạo thư mục output
# ===========================
os.makedirs("output_nlu", exist_ok=True)

# ===========================
# 5) Save model + vectorizer
# ===========================
joblib.dump(model, "output_nlu/intent_model.joblib")
joblib.dump(vectorizer, "output_nlu/tfidf.joblib")

print("🎉 Đã train lại NLU và tạo 2 file joblib trong thư mục output_nlu/")
