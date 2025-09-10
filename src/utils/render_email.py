from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Caminho base para templates
BASE = Path(__file__).parent / "template_email"

# Configuração do ambiente Jinja2
env = Environment(
    loader=FileSystemLoader(BASE),
    autoescape=select_autoescape(["html", "xml"]),
)

logger = logging.getLogger(__name__)

def render_email(start_dt: str, duration_seconds: str, captured: List[Dict], errors: List[str]) -> str:
    """
    Renderiza template de email simples (original)
    
    Args:
        start_dt: Data/hora de início no formato 'YYYY-MM-DD HH:MM:SS'
        duration_seconds: Duração no formato 'HH:MM:SS'
        captured: Lista de dicionários com dados dos pacientes processados
        errors: Lista de mensagens de erro
        
    Returns:
        str: HTML renderizado
    """
    try:
        template = env.get_template("summary.html")
        return template.render(
            start_dt=start_dt,
            duration=duration_seconds,
            captured=captured or [],
            errors=errors or []
        )
    except Exception as e:
        logger.error(f"Erro ao renderizar template summary.html: {e}")
        # Retorna template básico em caso de erro
        return _render_fallback_template(start_dt, duration_seconds, captured, errors)

def render_consolidated_email(start_dt: str, duration_seconds: str, data: Dict[str, Any]) -> str:
    """
    Renderiza template consolidado com dados das duas partes
    
    Args:
        start_dt: Data/hora de início no formato 'YYYY-MM-DD HH:MM:SS'
        duration_seconds: Duração no formato 'HH:MM:SS'
        data: Dicionário com estrutura:
            {
                "part1": {"captured": [...], "errors": [...], "not_found": [...]},
                "part2": {"captured": [...], "errors": [...], "not_found": [...]},
                "totals": {"captured": int, "errors": int, "not_found": int}
            }
            
    Returns:
        str: HTML renderizado
    """
    try:
        template = env.get_template("consolidated_summary.html")
        return template.render(
            start_dt=start_dt,
            duration=duration_seconds,
            data=data
        )
    except Exception as e:
        logger.error(f"Erro ao renderizar template consolidado: {e}")
        # Fallback para template simples combinando os dados
        all_captured = data.get("part1", {}).get("captured", []) + data.get("part2", {}).get("captured", [])
        all_errors = data.get("part1", {}).get("errors", []) + data.get("part2", {}).get("errors", [])
        return render_email(start_dt, duration_seconds, all_captured, all_errors)

def _render_fallback_template(start_dt: str, duration: str, captured: List[Dict], errors: List[str]) -> str:
    """
    Template básico de fallback em caso de erro nos templates principais
    """
    captured_html = ""
    if captured:
        captured_items = []
        for p in captured:
            captured_items.append(f"<li>{p.get('id', 'N/A')} - {p.get('name', 'N/A')} ({p.get('exam_date', 'N/A')})</li>")
        captured_html = f"<ul>{''.join(captured_items)}</ul>"
    else:
        captured_html = "<p>Nenhum paciente processado</p>"
    
    errors_html = ""
    if errors:
        error_items = [f"<li>{err}</li>" for err in errors]
        errors_html = f"<ul>{''.join(error_items)}</ul>"
    else:
        errors_html = "<p>Nenhum erro encontrado</p>"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Resumo de Scraping</title></head>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <h1>Resumo de Scraping</h1>
        <p><strong>Início:</strong> {start_dt}</p>
        <p><strong>Duração:</strong> {duration}</p>
        
        <h2>Pacientes Processados</h2>
        {captured_html}
        
        <h2>Erros</h2>
        {errors_html}
        
        <hr>
        <p style="font-size: 12px; color: #999;">
            Enviado por MatheusQa • {start_dt}
        </p>
    </body>
    </html>
    """

def validate_template_data(data: Dict[str, Any]) -> bool:
    """
    Valida se os dados estão no formato esperado para o template consolidado
    
    Args:
        data: Dados a serem validados
        
    Returns:
        bool: True se os dados são válidos
    """
    required_keys = ["part1", "part2", "totals"]
    
    if not all(key in data for key in required_keys):
        return False
    
    # Valida estrutura das partes
    for part in ["part1", "part2"]:
        part_data = data[part]
        if not isinstance(part_data, dict):
            return False
        
        required_part_keys = ["captured", "errors", "not_found"]
        if not all(key in part_data for key in required_part_keys):
            return False
        
        # Verifica se são listas
        for key in required_part_keys:
            if not isinstance(part_data[key], list):
                return False
    
    # Valida totals
    totals = data["totals"]
    if not isinstance(totals, dict):
        return False
    
    required_total_keys = ["captured", "errors", "not_found"]
    if not all(key in totals for key in required_total_keys):
        return False
    
    return True

def get_available_templates() -> List[str]:
    """
    Retorna lista de templates disponíveis
    
    Returns:
        List[str]: Lista de nomes dos templates
    """
    templates = []
    template_dir = Path(BASE)
    
    if template_dir.exists():
        for template_file in template_dir.glob("*.html"):
            templates.append(template_file.name)
    
    return templates

# Aliases para compatibilidade
render_summary_email = render_email
render_consolidated_summary = render_consolidated_email