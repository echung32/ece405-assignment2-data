#!/bin/bash
#SBATCH --job-name=wget-wiki
#SBATCH --account=bfdy-delta-cpu
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=2000M
#SBATCH --time=08:00:00
#SBATCH --output=logs/wget_%j.out
#SBATCH --error=logs/wget_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=echung32@hawaii.edu

echo "Cache generation job started on $(hostname) at $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Working directory: $SLURM_SUBMIT_DIR"
echo "CPUs allocated: $SLURM_CPUS_PER_TASK"
echo "Memory allocated: $SLURM_MEM_PER_CPU MB"

# Create logs directory if it doesn't exist
mkdir -p $SLURM_SUBMIT_DIR/logs

# Navigate to the working directory
cd $SLURM_SUBMIT_DIR

time wget --timeout=5 --waitretry=0 --tries=1 -i data/subsampled_positive_urls.txt --warc-file=data/subsampled_positive_urls -O /dev/null
