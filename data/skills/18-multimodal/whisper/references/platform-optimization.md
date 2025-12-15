# Platform-Specific Whisper Optimization

플랫폼별 고성능 Whisper 최적화 가이드.

---

## Windows/Linux (CUDA GPU)

### faster-whisper (권장)

**GitHub**: https://github.com/SYSTRAN/faster-whisper (12,000+ stars)

CTranslate2 기반 최적화 구현으로 원본 openai-whisper 대비 **4x 빠른 속도**, **메모리 사용량 감소**.

#### 설치

```bash
pip install faster-whisper
```

#### 기본 사용법

```python
from faster_whisper import WhisperModel

# GPU with FP16 (권장)
model = WhisperModel("large-v3", device="cuda", compute_type="float16")

# GPU with INT8 (메모리 절약)
# model = WhisperModel("large-v3", device="cuda", compute_type="int8_float16")

# CPU with INT8
# model = WhisperModel("large-v3", device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5)

print(f"Detected language: {info.language} ({info.language_probability:.2f})")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

#### 한국어 변환

```python
segments, info = model.transcribe(
    "korean_audio.mp3",
    language="ko",
    beam_size=5,
    vad_filter=True,  # 무음 구간 필터링
    vad_parameters=dict(min_silence_duration_ms=500)
)
```

#### Distil-Whisper (더 빠른 버전)

```python
# Distil 모델 사용 (6x 빠름, 정확도 약간 감소)
model = WhisperModel("distil-large-v3", device="cuda", compute_type="float16")

segments, info = model.transcribe(
    "audio.mp3",
    beam_size=5,
    language="en",
    condition_on_previous_text=False  # 긴 오디오시 hallucination 방지
)
```

#### 성능 비교

| 모델 | 속도 (RTF) | VRAM | 정확도 |
|------|-----------|------|--------|
| openai-whisper large-v3 | 1x | ~10GB | 기준 |
| faster-whisper large-v3 | **4x** | ~5GB | 동일 |
| distil-large-v3 | **6x** | ~3GB | -2% WER |

*RTF (Real-Time Factor): 낮을수록 빠름*

---

### whisper_streaming (실시간 스트리밍)

**GitHub**: https://github.com/ufal/whisper_streaming

실시간 음성 인식을 위한 스트리밍 파이프라인. faster-whisper 백엔드 지원.

#### 설치

```bash
pip install whisper-streaming
```

#### 기본 사용법

```python
from whisper_online import FasterWhisperASR, OnlineASRProcessor

# ASR 모델 로드
asr = FasterWhisperASR("en", "large-v2")

# 실시간 처리기 생성
online = OnlineASRProcessor(asr)

# 오디오 청크 처리 루프
while audio_has_not_ended:
    audio_chunk = receive_audio()  # 새 오디오 청크 수신
    online.insert_audio_chunk(audio_chunk)
    output = online.process_iter()
    print(output)  # 부분 결과 출력

# 마지막 결과
final_output = online.finish()
print(final_output)
```

#### CLI 사용

```bash
# 파일에서 실시간 시뮬레이션
python whisper_online.py audio.wav \
    --model large-v2 \
    --backend faster-whisper \
    --lan ko \
    --task transcribe

# VAD 활성화
python whisper_online.py audio.wav \
    --model large-v2 \
    --backend faster-whisper \
    --vad \
    --lan ko
```

#### 주요 옵션

| 옵션 | 설명 |
|------|------|
| `--backend` | `faster-whisper`, `whisper_timestamped`, `openai-api` |
| `--vad` | Voice Activity Detection 활성화 |
| `--task` | `transcribe` 또는 `translate` |
| `--buffer_trimming` | `sentence` 또는 `segment` |

---

### WhisperX (긴 오디오용)

**GitHub**: https://github.com/m-bain/whisperX

긴 오디오 파일 처리에 최적화. 화자 분리(diarization) 지원.

#### 설치

```bash
pip install whisperx
```

#### 기본 사용법

```python
import whisperx

device = "cuda"
audio_file = "long_audio.mp3"

# 모델 로드 및 변환
model = whisperx.load_model("large-v2", device, compute_type="float16")
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=16)

# 정렬 (더 정확한 타임스탬프)
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device)

# 화자 분리 (선택)
diarize_model = whisperx.DiarizationPipeline(use_auth_token="YOUR_HF_TOKEN", device=device)
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)
```

#### 특징

- **배치 처리**: 긴 오디오를 병렬 처리
- **단어 정렬**: wav2vec2 기반 정확한 타임스탬프
- **화자 분리**: pyannote.audio 통합
- **VAD 전처리**: 무음 구간 자동 제거

---

## Apple Silicon (M1/M2/M3/M4)

### Lightning-SimulWhisper (최고 성능)

**GitHub**: https://github.com/altalt-org/Lightning-SimulWhisper (335+ stars)

Apple Silicon 전용 MLX/CoreML 기반 구현. **최대 18x 인코딩, 15x 디코딩 속도 향상**.

#### 핵심 특징

| 특징 | 설명 |
|------|------|
| Zero PyTorch | Apple 생태계 순수 구현 (MLX + CoreML) |
| 실시간 스트리밍 | Simultaneous Speech Recognition 지원 |
| Neural Engine | CoreML로 Apple Neural Engine 가속 |
| 전력 효율 | CoreML 사용시 낮은 전력 소비 |
| AlignAtt 정책 | 최신 동시 디코딩 전략 적용 |

#### 설치

```bash
git clone https://github.com/altalt-org/Lightning-SimulWhisper.git
cd Lightning-SimulWhisper
pip install -r requirements.txt

# CoreML 가속 (권장)
pip install coremltools ane_transformers

# CoreML 모델 생성
git clone https://github.com/ggml-org/whisper.cpp.git
./scripts/generate_coreml_encoder.sh base.en
```

#### 사용법

```bash
# CoreML 가속 실행
python3 simulstreaming_whisper.py audio.wav \
    --model_name base.en \
    --model_path mlx_base \
    --use_coreml \
    --language en

# 한국어 실시간 변환
python simulstreaming_whisper.py test.mp3 \
    --language ko \
    --vac \
    --vad_silence_ms 1000 \
    --beams 3 \
    --model_name medium \
    --use_coreml \
    --coreml_compute_units CPU_AND_NE
```

#### 아키텍처

```
Audio Input (16kHz mono)
         ↓
Mel Spectrogram (MLX)
         ↓
┌─────────────────────────┐
│   CoreML Encoder        │ ← Apple Neural Engine (최대 18x)
└─────────────────────────┘
         ↓
┌─────────────────────────┐
│   MLX Decoder           │ ← Beam Search, AlignAtt
└─────────────────────────┘
         ↓
Transcription Output
```

#### 제한 사항

- Apple Silicon 전용 (Intel Mac, Linux, Windows 미지원)
- macOS 12 (Monterey) 이상 필요

---

### MLX Whisper

Apple MLX 프레임워크 기반 구현.

```bash
pip install mlx-whisper

mlx_whisper audio.mp3 --model base
```

---

## 크로스플랫폼 (Windows/Linux/Mac)

### whisper.cpp

**GitHub**: https://github.com/ggml-org/whisper.cpp (37,000+ stars)

C/C++ 구현으로 모든 플랫폼에서 빠른 성능.

#### 설치

```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp

# 기본 빌드
make

# CUDA 가속 (NVIDIA GPU)
make WHISPER_CUDA=1

# Metal 가속 (Apple GPU)
make WHISPER_METAL=1

# 모델 다운로드
./models/download-ggml-model.sh base.en
```

#### 사용법

```bash
# 기본 실행
./main -m models/ggml-base.en.bin -f audio.wav

# 한국어
./main -m models/ggml-medium.bin -l ko -f korean.wav

# 실시간 스트리밍
./stream -m models/ggml-base.en.bin
```

---

## 플랫폼별 권장 도구

| 플랫폼 | 실시간 스트리밍 | 배치 처리 | 긴 오디오 |
|--------|----------------|-----------|-----------|
| **Windows (CUDA)** | whisper_streaming + faster-whisper | faster-whisper | WhisperX |
| **Linux (CUDA)** | whisper_streaming + faster-whisper | faster-whisper | WhisperX |
| **Apple Silicon** | **Lightning-SimulWhisper** | MLX Whisper | faster-whisper |
| **CPU only** | whisper.cpp | whisper.cpp | openai-whisper |

---

## 성능 비교 요약

| 도구 | 플랫폼 | 속도 | 실시간 | 특징 |
|------|--------|------|--------|------|
| **Lightning-SimulWhisper** | Apple Silicon | 최고 (18x) | O | CoreML/MLX, 전력 효율 |
| **faster-whisper** | CUDA GPU | 빠름 (4x) | X | CTranslate2, 범용 |
| **whisper_streaming** | CUDA GPU | 빠름 | O | 실시간 파이프라인 |
| **WhisperX** | CUDA GPU | 빠름 | X | 화자 분리, 긴 오디오 |
| **whisper.cpp** | 모든 플랫폼 | 빠름 | O | C++ 구현, 경량 |
| **openai-whisper** | 모든 플랫폼 | 기준 | X | 공식 구현, 안정 |

---

## 참고 자료

### Windows/Linux
- **faster-whisper**: https://github.com/SYSTRAN/faster-whisper
- **whisper_streaming**: https://github.com/ufal/whisper_streaming
- **WhisperX**: https://github.com/m-bain/whisperX

### Apple Silicon
- **Lightning-SimulWhisper**: https://github.com/altalt-org/Lightning-SimulWhisper
- **MLX Whisper**: https://github.com/ml-explore/mlx-examples/tree/main/whisper
- **PyTorch KR 소개글**: https://discuss.pytorch.kr/t/lightning-simulwhisper-apple-silicon-feat-whisper/8070

### 크로스플랫폼
- **whisper.cpp**: https://github.com/ggml-org/whisper.cpp
- **openai-whisper**: https://github.com/openai/whisper
