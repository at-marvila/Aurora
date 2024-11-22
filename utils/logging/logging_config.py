import logging
import sys
import warnings

def setup_logging(log_to_file: bool = False, log_file: str = "aurora.log"):
    """Configuração central de logging para Aurora."""
    if len(logging.root.handlers) > 0:
        # Evita reconfigurar logging se já estiver configurado
        return

    # Suprimir warnings desnecessários
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*torch.cuda.amp.custom_fwd.*")
    warnings.filterwarnings("ignore", message=".*speechbrain.pretrained.*")
    warnings.filterwarnings("ignore", message=".*torch.load.*")

    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_to_file:
        handlers.append(logging.FileHandler(log_file, mode="a", encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
    )

    noisy_modules = ["huggingface", "torch", "transformers", "speechbrain"]
    for module in noisy_modules:
        logging.getLogger(module).setLevel(logging.WARNING)

    logging.info("=" * 50)
    logging.info("Iniciando Aurora AI System...")
    logging.info("=" * 50)