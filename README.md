# ECG Compression Benchmark

## Project Overview

This project is an ECG (Electrocardiogram) signal compression algorithm evaluation platform based on Codabench. Researchers can upload their compression algorithms and automatically evaluate the Compression Ratio (CR) and Percentage Root Mean Square Difference (PRD) on private datasets.

## Project Structure


```plaintext
ECG_Compression_Benchmark/
├── Development_Phase/       # Development phase data
│   ├── input_data/          # Input data (for local testing)
│   └── reference_data/      # Reference data (local test labels)
├── Final_Phase/             # Final phase data
│   ├── input_data/          # Input data
│   └── reference_data/      # Reference data
├── ingestion_program/       # Evaluation entry program
│   ├── ingestion.py         # Script to run participant code
│   └── metadata.yaml        # Configuration file
├── scoring_program/         # Scoring program
│   ├── scoring.py           # Script to compute scores
│   └── metadata.yaml        # Configuration file
├── pages/                   # Documentation pages
|   ├── data.md           
|   ├── terms.md             # Terms and conditions
|   ├── overview.md              
|   ├── evaluation/
├── competition.yaml        # Global configuration file
└──      
```
## Quick Start

### 1. Local Development

1. Clone the repository:
    
   ```plaintext
   git clone https://github.com/your-username/ECG_Compression_Benchmark.git
   cd ECG_Compression_Benchmark
   ```
    
2. Install dependencies:
    
    ```plaintext
    pip install -r requirements.txt
    ```
3. Run local tests:
    
    
    # Run ingestion_program
   ```plaintext
    python ingestion_program/ingestion.py Development_Phase/input_data output
   ```
    # Run scoring_program
   ```plaintext
    python scoring_program/scoring.py Development_Phase/input_data output scores
   ```

### 2. Submitting to Codabench

1. Download the participant template:
    
    - Package the `solution/` directory into `solution.zip`:
        ```plaintext
        cd solution
        zip solution.zip *
        ```
2. Upload to Codabench:
    
    - On the Codabench My Submission page, upload `solution.zip` as a participant submission.
        

## Scoring Logic

The scoring is based on the following metrics:

- **Compression Ratio (CR)**: The ratio of the original signal length to the compressed signal length.
    
- **Percentage Root Mean Square Difference (PRD)**: The error percentage between the reconstructed signal and the original signal.
    
- **Overall Score**: `Score = CR / (PRD + ε)`, where `ε` is a small value (e.g., `1e-6`).
    

## Participation Guide

1. Download the participant template (`solution.zip`).
    
2. Implement the `ECGCompressor` class in `ecg_model.py`.
    
3. Submit your code to Codabench and view the scoring results.
    

## Contributing

We welcome contributions! Please submit Issues or Pull Requests to improve this project.

## License

This project is open-source under the MIT License. See the [LICENSE](https://license/) file for details.

---
