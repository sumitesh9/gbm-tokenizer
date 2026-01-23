.PHONY: activate install train infer clean help

# Activate the virtual environment in an interactive shell
activate:
	@echo "Activating virtual environment..."
	@bash -c "source venv/bin/activate && exec bash"

# Install dependencies (if requirements.txt exists)
install:
	@if [ -f requirements.txt ]; then \
		venv/bin/pip install -r requirements.txt; \
	else \
		echo "No requirements.txt found. Skipping install."; \
	fi

# Train the tokenizer using train.py
train:
	@echo "Training tokenizer..."
	@venv/bin/python train.py

# Run inference using infer.py
infer:
	@echo "Running inference..."
	@venv/bin/python infer.py

# Clean up Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true

# Show help message
help:
	@echo "Available commands:"
	@echo "  make activate  - Activate the virtual environment in an interactive shell"
	@echo "  make install   - Install dependencies from requirements.txt"
	@echo "  make train     - Train the tokenizer using train.py"
	@echo "  make infer     - Run inference using infer.py"
	@echo "  make clean     - Remove Python cache files"
	@echo "  make help      - Show this help message"
