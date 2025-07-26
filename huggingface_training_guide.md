# Hugging Face 模型训练完整指南

> 本指南提供了使用Hugging Face进行模型训练的完整流程，包含实用代码示例和最佳实践。

## 目录
1. [环境准备](#环境准备)
2. [数据准备](#数据准备)
3. [模型选择与配置](#模型选择与配置)
4. [训练流程](#训练流程)
5. [模型评估](#模型评估)
6. [模型保存与部署](#模型保存与部署)
7. [高级技巧](#高级技巧)
8. [常见问题与解决方案](#常见问题与解决方案)
9. [参考资源](#参考资源)

## 环境准备

### 1. 系统要求
- Python 3.7+
- CUDA 11.0+ (GPU训练推荐)
- 内存: 8GB+ (取决于模型大小)

### 2. 安装必要的库
```bash
# 基础安装
pip install transformers datasets torch accelerate wandb

# 可选依赖
pip install tensorboard scikit-learn pandas matplotlib seaborn

# GPU支持 (如果有NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. 验证安装
```python
import torch
import transformers
print(f"PyTorch版本: {torch.__version__}")
print(f"Transformers版本: {transformers.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU数量: {torch.cuda.device_count()}")
```

### 4. 导入必要的模块
```python
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    TrainingArguments, 
    Trainer,
    DataCollatorWithPadding,
    EarlyStoppingCallback
)
from datasets import Dataset, load_dataset
import torch
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import wandb
import os
```

## 数据准备

### 1. 数据格式要求

训练数据支持多种格式：

#### CSV格式示例
```csv
text,label
"这是一个正面评价",1
"这个产品很糟糕",0
```

#### JSON格式示例
```json
{"text": "这是一个正面评价", "label": 1}
{"text": "这个产品很糟糕", "label": 0}
```

#### 文本分类标签映射
```python
label_mapping = {
    0: "负面",
    1: "正面"
}
```

### 2. 数据加载与预处理

```python
def load_custom_dataset(file_path, file_type="csv"):
    """
    加载自定义数据集
    
    Args:
        file_path: 数据文件路径
        file_type: 文件类型 ('csv', 'json', 'txt')
    
    Returns:
        Dataset: Hugging Face Dataset对象
    """
    if file_type == "csv":
        df = pd.read_csv(file_path)
        dataset = Dataset.from_pandas(df)
    elif file_type == "json":
        dataset = load_dataset('json', data_files=file_path, split='train')
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")
    
    return dataset

def preprocess_function(examples, tokenizer, max_length=512):
    """
    数据预处理函数
    
    Args:
        examples: 批量样本
        tokenizer: 分词器
        max_length: 最大序列长度
    
    Returns:
        dict: 处理后的数据
    """
    # 文本编码
    encoding = tokenizer(
        examples['text'], 
        truncation=True, 
        padding=True, 
        max_length=max_length,
        return_tensors="pt"
    )
    
    # 添加标签
    if 'label' in examples:
        encoding['labels'] = examples['label']
    
    return encoding

def clean_text(text):
    """
    文本清洗函数
    """
    import re
    # 移除特殊字符
    text = re.sub(r'[^\w\s]', '', text)
    # 移除多余空格
    text = ' '.join(text.split())
    return text.strip()
```

### 3. 数据集划分与验证

```python
def split_dataset(dataset, test_size=0.2, val_size=0.1, random_state=42):
    """
    划分数据集为训练集、验证集和测试集
    
    Args:
        dataset: 原始数据集
        test_size: 测试集比例
        val_size: 验证集比例
        random_state: 随机种子
    
    Returns:
        tuple: (train_dataset, val_dataset, test_dataset)
    """
    # 首先分离出测试集
    train_val_dataset, test_dataset = dataset.train_test_split(
        test_size=test_size, 
        seed=random_state
    ).values()
    
    # 从训练集中分离出验证集
    train_dataset, val_dataset = train_val_dataset.train_test_split(
        test_size=val_size/(1-test_size), 
        seed=random_state
    ).values()
    
    print(f"训练集大小: {len(train_dataset)}")
    print(f"验证集大小: {len(val_dataset)}")
    print(f"测试集大小: {len(test_dataset)}")
    
    return train_dataset, val_dataset, test_dataset

def analyze_dataset(dataset):
    """
    分析数据集统计信息
    """
    if 'label' in dataset.column_names:
        labels = dataset['label']
        unique_labels = set(labels)
        print(f"标签分布:")
        for label in unique_labels:
            count = labels.count(label)
            print(f"  标签 {label}: {count} 样本 ({count/len(labels)*100:.1f}%)")
    
    # 文本长度分析
    text_lengths = [len(text.split()) for text in dataset['text']]
    print(f"\n文本长度统计:")
    print(f"  平均长度: {np.mean(text_lengths):.1f} 词")
    print(f"  最大长度: {max(text_lengths)} 词")
    print(f"  最小长度: {min(text_lengths)} 词")
```

## 模型选择与配置

### 1. 预训练模型选择指南

```python
# 中文模型推荐
chinese_models = {
    'bert-base': 'bert-base-chinese',  # 通用，稳定
    'roberta': 'hfl/chinese-roberta-wwm-ext',  # 性能优秀
    'electra': 'hfl/chinese-electra-180g-base-discriminator',  # 效率高
    'macbert': 'hfl/chinese-macbert-base',  # 改进版BERT
    'ernie': 'nghuyong/ernie-1.0-base-zh'  # 百度开源
}

# 英文模型推荐
english_models = {
    'bert-base': 'bert-base-uncased',
    'roberta': 'roberta-base',
    'distilbert': 'distilbert-base-uncased',  # 轻量级
    'albert': 'albert-base-v2'  # 参数共享
}

# 多语言模型
multilingual_models = {
    'mbert': 'bert-base-multilingual-cased',
    'xlm-roberta': 'xlm-roberta-base'
}
```

### 2. 模型初始化

```python
def initialize_model_and_tokenizer(model_name, num_labels=2, task_type="classification"):
    """
    初始化模型和分词器
    
    Args:
        model_name: 预训练模型名称
        num_labels: 分类任务的标签数量
        task_type: 任务类型 ('classification', 'generation')
    
    Returns:
        tuple: (model, tokenizer)
    """
    # 初始化分词器
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # 根据任务类型选择模型
    if task_type == "classification":
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels,
            problem_type="single_label_classification"
        )
    elif task_type == "generation":
        model = AutoModelForCausalLM.from_pretrained(model_name)
    else:
        raise ValueError(f"不支持的任务类型: {task_type}")
    
    # 添加特殊token（如果需要）
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id
    
    print(f"模型参数量: {model.num_parameters():,}")
    print(f"词汇表大小: {len(tokenizer)}")
    
    return model, tokenizer

# 使用示例
model_name = chinese_models['roberta']
model, tokenizer = initialize_model_and_tokenizer(model_name, num_labels=2)
```

### 3. 模型配置优化

```python
def configure_model_for_training(model, learning_rate=2e-5, dropout_rate=0.1):
    """
    配置模型训练参数
    """
    # 设置dropout
    if hasattr(model.config, 'hidden_dropout_prob'):
        model.config.hidden_dropout_prob = dropout_rate
    if hasattr(model.config, 'attention_probs_dropout_prob'):
        model.config.attention_probs_dropout_prob = dropout_rate
    
    # 冻结部分层（可选）
    # freeze_layers(model, num_layers_to_freeze=6)
    
    return model

def freeze_layers(model, num_layers_to_freeze=6):
    """
    冻结模型的前几层
    """
    if hasattr(model, 'bert'):
        layers = model.bert.encoder.layer
    elif hasattr(model, 'roberta'):
        layers = model.roberta.encoder.layer
    else:
        print("无法识别模型类型，跳过层冻结")
        return
    
    for i in range(min(num_layers_to_freeze, len(layers))):
        for param in layers[i].parameters():
            param.requires_grad = False
    
    print(f"已冻结前 {num_layers_to_freeze} 层")
```

## 训练流程

### 1. 训练参数配置

```python
def create_training_arguments(output_dir="./results", **kwargs):
    """
    创建训练参数配置
    """
    default_args = {
        "output_dir": output_dir,
        "num_train_epochs": 3,
        "per_device_train_batch_size": 16,
        "per_device_eval_batch_size": 32,
        "warmup_steps": 500,
        "weight_decay": 0.01,
        "learning_rate": 2e-5,
        "logging_dir": f"{output_dir}/logs",
        "logging_steps": 100,
        "evaluation_strategy": "steps",
        "eval_steps": 500,
        "save_strategy": "steps",
        "save_steps": 500,
        "save_total_limit": 3,
        "load_best_model_at_end": True,
        "metric_for_best_model": "eval_accuracy",
        "greater_is_better": True,
        "report_to": "wandb",  # 使用wandb记录
        "run_name": f"huggingface-training-{pd.Timestamp.now().strftime('%Y%m%d-%H%M%S')}",
        "dataloader_num_workers": 4,
        "fp16": torch.cuda.is_available(),  # 混合精度训练
        "gradient_checkpointing": True,  # 节省显存
    }
    
    # 更新自定义参数
    default_args.update(kwargs)
    
    return TrainingArguments(**default_args)
```

### 2. 评估指标定义

```python
def compute_metrics(eval_pred):
    """
    计算评估指标
    """
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    # 计算基础指标
    accuracy = accuracy_score(labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average='weighted'
    )
    
    # 详细分类报告
    report = classification_report(
        labels, predictions, 
        target_names=[f"类别_{i}" for i in range(len(set(labels)))],
        output_dict=True
    )
    
    return {
        'accuracy': accuracy,
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'macro_f1': report['macro avg']['f1-score'],
        'weighted_f1': report['weighted avg']['f1-score']
    }
```

### 3. 完整训练流程

```python
def train_model(model, tokenizer, train_dataset, eval_dataset, training_args):
    """
    执行模型训练
    """
    # 数据预处理
    train_dataset = train_dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=train_dataset.column_names
    )
    
    eval_dataset = eval_dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=eval_dataset.column_names
    )
    
    # 数据整理器
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    # 初始化Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    # 开始训练
    print("开始训练...")
    trainer.train()
    
    # 保存最佳模型
    trainer.save_model()
    tokenizer.save_pretrained(training_args.output_dir)
    
    return trainer

# 训练示例
if __name__ == "__main__":
    # 初始化wandb
    wandb.init(project="huggingface-training")
    
    # 加载数据
    dataset = load_custom_dataset("data/train.csv")
    train_ds, val_ds, test_ds = split_dataset(dataset)
    
    # 初始化模型
    model, tokenizer = initialize_model_and_tokenizer(
        chinese_models['roberta'], 
        num_labels=2
    )
    
    # 创建训练参数
    training_args = create_training_arguments(
        output_dir="./results",
        num_train_epochs=5,
        per_device_train_batch_size=8
    )
    
    # 训练模型
    trainer = train_model(model, tokenizer, train_ds, val_ds, training_args)
```

## 模型评估

### 1. 全面评估函数

```python
def evaluate_model(trainer, test_dataset, tokenizer):
    """
    全面评估模型性能
    """
    # 预处理测试数据
    test_dataset = test_dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=test_dataset.column_names
    )
    
    # 评估
    eval_results = trainer.evaluate(test_dataset)
    
    print("=== 模型评估结果 ===")
    for key, value in eval_results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    return eval_results

def predict_single_text(model, tokenizer, text, device="cuda"):
    """
    单文本预测
    """
    model.eval()
    inputs = tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        padding=True, 
        max_length=512
    ).to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = torch.argmax(predictions, dim=-1).item()
        confidence = predictions[0][predicted_class].item()
    
    return predicted_class, confidence

def batch_predict(model, tokenizer, texts, batch_size=32):
    """
    批量预测
    """
    model.eval()
    predictions = []
    confidences = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = model(**inputs)
            batch_predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            batch_classes = torch.argmax(batch_predictions, dim=-1)
            batch_confidences = torch.max(batch_predictions, dim=-1)[0]
            
            predictions.extend(batch_classes.cpu().numpy())
            confidences.extend(batch_confidences.cpu().numpy())
    
    return predictions, confidences
```

### 2. 可视化分析

```python
def plot_training_history(trainer):
    """
    绘制训练历史
    """
    import matplotlib.pyplot as plt
    
    log_history = trainer.state.log_history
    
    # 提取训练和验证指标
    train_loss = [log['train_loss'] for log in log_history if 'train_loss' in log]
    eval_loss = [log['eval_loss'] for log in log_history if 'eval_loss' in log]
    eval_accuracy = [log['eval_accuracy'] for log in log_history if 'eval_accuracy' in log]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # 损失曲线
    ax1.plot(train_loss, label='训练损失')
    ax1.plot(eval_loss, label='验证损失')
    ax1.set_title('损失曲线')
    ax1.set_xlabel('步数')
    ax1.set_ylabel('损失')
    ax1.legend()
    
    # 准确率曲线
    ax2.plot(eval_accuracy, label='验证准确率')
    ax2.set_title('准确率曲线')
    ax2.set_xlabel('步数')
    ax2.set_ylabel('准确率')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_confusion_matrix(y_true, y_pred, class_names=None):
    """
    绘制混淆矩阵
    """
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d', 
        cmap='Blues',
        xticklabels=class_names or range(len(cm)),
        yticklabels=class_names or range(len(cm))
    )
    plt.title('混淆矩阵')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
```

## 模型保存与部署

### 1. 模型保存

```python
def save_model_for_production(model, tokenizer, save_path, model_info=None):
    """
    保存生产环境模型
    """
    import json
    from datetime import datetime
    
    # 创建保存目录
    os.makedirs(save_path, exist_ok=True)
    
    # 保存模型和分词器
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    
    # 保存模型信息
    if model_info is None:
        model_info = {
            "model_name": model.config.name_or_path,
            "num_labels": model.config.num_labels,
            "max_length": tokenizer.model_max_length,
            "vocab_size": len(tokenizer),
            "save_time": datetime.now().isoformat(),
            "framework": "transformers"
        }
    
    with open(os.path.join(save_path, "model_info.json"), "w", encoding="utf-8") as f:
        json.dump(model_info, f, ensure_ascii=False, indent=2)
    
    print(f"模型已保存到: {save_path}")

def load_model_for_inference(model_path):
    """
    加载模型用于推理
    """
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # 加载模型信息
    info_path = os.path.join(model_path, "model_info.json")
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            model_info = json.load(f)
        print(f"模型信息: {model_info}")
    
    return model, tokenizer
```

### 2. 模型量化与优化

```python
def quantize_model(model, tokenizer, save_path):
    """
    模型量化以减小大小和提高推理速度
    """
    from transformers import pipeline
    
    # 动态量化
    quantized_model = torch.quantization.quantize_dynamic(
        model, 
        {torch.nn.Linear}, 
        dtype=torch.qint8
    )
    
    # 保存量化模型
    torch.save(quantized_model.state_dict(), os.path.join(save_path, "quantized_model.pth"))
    tokenizer.save_pretrained(save_path)
    
    print(f"量化模型已保存到: {save_path}")
    return quantized_model

def create_inference_pipeline(model_path):
    """
    创建推理管道
    """
    from transformers import pipeline
    
    classifier = pipeline(
        "text-classification",
        model=model_path,
        tokenizer=model_path,
        device=0 if torch.cuda.is_available() else -1
    )
    
    return classifier
```

### 3. API部署示例

```python
# 使用FastAPI部署模型
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="文本分类API")

# 全局变量存储模型
model = None
tokenizer = None

class TextInput(BaseModel):
    text: str
    max_length: int = 512

class PredictionOutput(BaseModel):
    predicted_class: int
    confidence: float
    probabilities: dict

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    model, tokenizer = load_model_for_inference("./best_model")
    model.eval()
    print("模型加载完成")

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: TextInput):
    predicted_class, confidence = predict_single_text(
        model, tokenizer, input_data.text
    )
    
    # 获取所有类别的概率
    inputs = tokenizer(
        input_data.text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=input_data.max_length
    )
    
    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        prob_dict = {f"class_{i}": float(prob) for i, prob in enumerate(probabilities[0])}
    
    return PredictionOutput(
        predicted_class=predicted_class,
        confidence=confidence,
        probabilities=prob_dict
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 高级技巧

### 1. 学习率调度

```python
from transformers import get_linear_schedule_with_warmup, get_cosine_schedule_with_warmup

def create_scheduler(optimizer, num_training_steps, warmup_steps=None, schedule_type="linear"):
    """
    创建学习率调度器
    """
    if warmup_steps is None:
        warmup_steps = num_training_steps // 10
    
    if schedule_type == "linear":
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=num_training_steps
        )
    elif schedule_type == "cosine":
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=num_training_steps
        )
    else:
        raise ValueError(f"不支持的调度类型: {schedule_type}")
    
    return scheduler
```

### 2. 数据增强

```python
import random

def augment_text(text, augment_prob=0.1):
    """
    简单的文本数据增强
    """
    words = text.split()
    augmented_words = []
    
    for word in words:
        if random.random() < augment_prob:
            # 随机删除词汇
            if random.random() < 0.3:
                continue
            # 随机重复词汇
            elif random.random() < 0.3:
                augmented_words.extend([word, word])
            else:
                augmented_words.append(word)
        else:
            augmented_words.append(word)
    
    return " ".join(augmented_words)

def create_augmented_dataset(dataset, augment_ratio=0.2):
    """
    创建增强数据集
    """
    augmented_data = []
    
    for example in dataset:
        # 原始数据
        augmented_data.append(example)
        
        # 增强数据
        if random.random() < augment_ratio:
            augmented_text = augment_text(example['text'])
            augmented_example = example.copy()
            augmented_example['text'] = augmented_text
            augmented_data.append(augmented_example)
    
    return Dataset.from_list(augmented_data)
```

### 3. 多GPU训练

```python
def setup_multi_gpu_training():
    """
    设置多GPU训练
    """
    if torch.cuda.device_count() > 1:
        print(f"使用 {torch.cuda.device_count()} 个GPU进行训练")
        return True
    return False

# 在TrainingArguments中添加
training_args = TrainingArguments(
    # ... 其他参数
    dataloader_num_workers=4,
    ddp_find_unused_parameters=False,  # 提高多GPU效率
    per_device_train_batch_size=8,
    gradient_accumulation_steps=2,  # 等效batch_size = 8 * 2 * num_gpus
)
```

## 常见问题与解决方案

### 1. 内存不足问题

**问题**: CUDA out of memory

**解决方案**:
```python
# 1. 减小batch size
training_args.per_device_train_batch_size = 4
training_args.per_device_eval_batch_size = 8

# 2. 使用梯度累积
training_args.gradient_accumulation_steps = 4

# 3. 启用梯度检查点
training_args.gradient_checkpointing = True

# 4. 使用混合精度训练
training_args.fp16 = True

# 5. 清理GPU缓存
torch.cuda.empty_cache()
```

### 2. 训练速度慢

**解决方案**:
```python
# 1. 使用更多数据加载器工作进程
training_args.dataloader_num_workers = 8

# 2. 启用编译优化（PyTorch 2.0+）
model = torch.compile(model)

# 3. 使用更高效的优化器
from transformers import AdamW
optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
```

### 3. 模型过拟合

**解决方案**:
```python
# 1. 增加dropout
model.config.hidden_dropout_prob = 0.2
model.config.attention_probs_dropout_prob = 0.2

# 2. 使用权重衰减
training_args.weight_decay = 0.01

# 3. 早停
from transformers import EarlyStoppingCallback
callbacks = [EarlyStoppingCallback(early_stopping_patience=3)]

# 4. 数据增强
train_dataset = create_augmented_dataset(train_dataset)
```

### 4. 模型欠拟合

**解决方案**:
```python
# 1. 增加训练轮数
training_args.num_train_epochs = 10

# 2. 调整学习率
training_args.learning_rate = 5e-5

# 3. 减少正则化
training_args.weight_decay = 0.001

# 4. 使用更大的模型
model_name = 'hfl/chinese-roberta-wwm-ext-large'
```

### 5. 分词器问题

```python
# 处理特殊字符
def clean_and_tokenize(text, tokenizer):
    # 清理文本
    text = text.strip()
    text = ' '.join(text.split())  # 规范化空格
    
    # 检查长度
    tokens = tokenizer.tokenize(text)
    if len(tokens) > tokenizer.model_max_length - 2:  # 留出特殊token空间
        tokens = tokens[:tokenizer.model_max_length - 2]
        text = tokenizer.convert_tokens_to_string(tokens)
    
    return text
```

### 6. 模型推理优化

```python
def optimize_for_inference(model):
    """
    优化模型用于推理
    """
    model.eval()
    
    # 禁用梯度计算
    for param in model.parameters():
        param.requires_grad = False
    
    # 使用TorchScript（可选）
    # model = torch.jit.script(model)
    
    return model

# 批量推理优化
def efficient_batch_inference(model, tokenizer, texts, batch_size=32):
    """
    高效批量推理
    """
    model.eval()
    results = []
    
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # 批量编码
            inputs = tokenizer(
                batch,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512
            )
            
            # 推理
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            results.extend(predictions.cpu().numpy())
    
    return results
```

## 参考资源

### 官方文档
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [Hugging Face Datasets](https://huggingface.co/docs/datasets/index)
- [PyTorch官方文档](https://pytorch.org/docs/stable/index.html)

### 推荐阅读
- [BERT论文](https://arxiv.org/abs/1810.04805)
- [RoBERTa论文](https://arxiv.org/abs/1907.11692)
- [ELECTRA论文](https://arxiv.org/abs/2003.10555)

### 实用工具
- [Weights & Biases](https://wandb.ai/) - 实验跟踪
- [TensorBoard](https://www.tensorflow.org/tensorboard) - 可视化
- [Gradio](https://gradio.app/) - 快速构建演示界面

### 社区资源
- [Hugging Face Hub](https://huggingface.co/models) - 预训练模型
- [Papers with Code](https://paperswithcode.com/) - 论文和代码
- [GitHub Transformers](https://github.com/huggingface/transformers) - 源码

---

> **提示**: 本指南提供了完整的Hugging Face模型训练流程，建议根据具体任务需求调整参数和配置。如有问题，请参考官方文档或社区讨论。