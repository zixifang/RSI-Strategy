# 可选：课程服务器上用 Slurm 跑同一条冒烟命令。
# 第 1 周不依赖集群。分区名、账号按学校集群说明修改。
#SBATCH --job-name=rsi-backtest
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=output/slurm-%j.out

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-.}"

python -m pip install -r requirements.txt
python -m pytest
python -m src.main
