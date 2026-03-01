# Plataforma de Mineração Simulada (Python + Tkinter)

Estrutura MVP em **Python com Tkinter**, simulando um sistema com:

- cadastro/login simples
- depósito e ativação de saldo
- contratação de máquinas virtuais (planos)
- rendimentos diários automáticos
- moeda interna indexada (1 USD da plataforma = R$ 6,00)
- solicitação de saque com valor mínimo
- dashboard com métricas, contratos e movimentações

## Fluxo implementado

- **Cadastro/Login**: entrada com nome, e-mail e senha para acessar o painel.
- **Depósito**: entrada em BRL e conversão para USD da plataforma.
- **Máquinas**: contratação de plano com valor, prazo, lucro diário e retorno previsto.
- **Rendimentos**: crédito automático por dias corridos desde o último payout.
- **Saque**: solicitação com validação de saldo e valor mínimo (`US$ 20,00`).

## Como executar

1. Tenha Python 3.10+ instalado.
2. Execute:

```bash
python main.py
```

> Tkinter já acompanha a instalação padrão do Python na maioria dos ambientes Windows.

## Estrutura de pastas

- `main.py`: ponto de entrada da aplicação.
- `tkinter_app/app.py`: interface gráfica (login, abas e dashboard).
- `tkinter_app/core.py`: regras de negócio e estado da plataforma.
- `tkinter_app/constants.py`: planos e parâmetros fixos.
- `tkinter_app/utils.py`: conversões de moeda, datas e formatação.

## Observação

Este projeto é uma simulação educacional e não integra autenticação real, gateways de pagamento, KYC ou liquidação financeira.
