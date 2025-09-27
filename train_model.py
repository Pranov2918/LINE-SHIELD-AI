import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical

# --- 1. Load Data ---
print("🧠 Loading data...")
df = pd.read_csv('fault_data.csv')
X = df.drop('label', axis=1).values
y = df['label'].values

# --- 2. Preprocess Data ---
X = X.reshape(X.shape[0], X.shape[1], 1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
y_train_cat = to_categorical(y_train)
y_test_cat = to_categorical(y_test)

# --- 3. Build Model ---
print("🛠️ Building 1D-CNN model...")
model = Sequential([
    Conv1D(filters=32, kernel_size=5, activation='relu', input_shape=(X_train.shape[1], 1)),
    MaxPooling1D(pool_size=2),
    Dropout(0.3),
    Conv1D(filters=64, kernel_size=5, activation='relu'),
    MaxPooling1D(pool_size=2),
    Dropout(0.3),
    Flatten(),
    Dense(100, activation='relu'),
    Dense(y_train_cat.shape[1], activation='softmax')
])
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# --- 4. Train Model ---
print("💪 Training model...")
model.fit(X_train, y_train_cat, epochs=10, batch_size=32, validation_split=0.1)

# --- 5. Evaluate Model ---
print("📊 Evaluating model...")
loss, accuracy = model.evaluate(X_test, y_test_cat)
print(f"✅ Test Accuracy: {accuracy * 100:.2f}%")

# --- 6. Save Model ---
model.save('line_shield_model.h5')
print("✅ Model saved as line_shield_model.h5")