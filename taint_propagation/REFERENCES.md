# Taint Analysis - Официальная документация

Все анимации основаны на официальной документации LLVM/Clang и академических источниках.

## 1. Clang Static Analyzer - Taint Analysis Configuration
**URL:** https://clang.llvm.org/docs/analyzer/user-docs/TaintAnalysisConfiguration.html

### Ключевые цитаты:
- "The Clang Static Analyzer uses taint analysis to detect injection vulnerability related issues in code"
- "Taint analysis defines **sources**, **sinks**, and **propagation rules**"
- "It identifies errors by detecting a flow of information that originates from a taint source, reaches a taint sink"

### YAML конфигурация:
```yaml
Sources:
  - kind: call
    method: <METHOD_SIGNATURE>
    index: <INDEX>

Propagations:
  - method: <METHOD_SIGNATURE>
    SrcArgs: 
    DstArgs: [-1]

Sinks:
  - method: system
    Args: 
