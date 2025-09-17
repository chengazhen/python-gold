# GitHub Actions 注意事项

## 🚨 重要：变量命名规则

### ❌ 禁止使用的变量名前缀

GitHub Actions中以下前缀的变量名是**保留的**，不能作为自定义环境变量使用：

- `GITHUB_*` - GitHub保留变量
- `RUNNER_*` - Runner保留变量  
- `ACTIONS_*` - Actions保留变量

### ✅ 正确的使用方式

#### 1. 使用GitHub内置变量
```yaml
# ✅ 正确 - 使用内置的GitHub变量
- name: 获取仓库信息
  run: |
    echo "仓库: ${{ github.repository }}"
    echo "分支: ${{ github.ref }}"
    echo "提交: ${{ github.sha }}"
```

#### 2. 使用GitHub Secrets
```yaml
# ✅ 正确 - 使用GitHub Token
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}

# ✅ 正确 - 使用自定义Secret
- uses: some-action@v1
  with:
    api_key: ${{ secrets.MY_API_KEY }}
```

#### 3. 使用GitHub输出变量
```yaml
# ✅ 正确 - 设置输出变量
- name: 检查变化
  id: check
  run: |
    echo "has_changes=true" >> $GITHUB_OUTPUT
    
# ✅ 正确 - 使用输出变量
- name: 使用结果
  if: steps.check.outputs.has_changes == 'true'
  run: echo "有变化"
```

#### 4. 自定义环境变量
```yaml
# ✅ 正确 - 使用自定义前缀
- name: 设置变量
  run: |
    MY_DATE=$(date '+%Y-%m-%d')
    GOLD_COUNT=$(jq length data.json)
    echo "MY_DATE=${MY_DATE}" >> $GITHUB_ENV
    echo "GOLD_COUNT=${GOLD_COUNT}" >> $GITHUB_ENV
```

### ❌ 错误示例

```yaml
# ❌ 错误 - 不能使用GITHUB_开头的自定义变量
- name: 错误示例
  run: |
    GITHUB_MY_VAR="value"  # 这会失败！
    export GITHUB_MY_VAR
```

## 🔧 我们项目中的修复

### 修复前的问题
原来的工作流文件可能包含：
- YAML语法错误（多余空格）
- 不正确的token引用

### 修复后的改进
1. **修复了YAML语法错误**
   ```yaml
   # 修复前
   run: |  # 多余空格导致错误
   
   # 修复后  
   run: |
   ```

2. **使用正确的GitHub Token**
   ```yaml
   # ✅ 正确
   token: ${{ secrets.GITHUB_TOKEN }}
   github_token: ${{ secrets.GITHUB_TOKEN }}
   ```

3. **使用标准的输出变量**
   ```yaml
   # ✅ 正确
   echo "has_changes=true" >> $GITHUB_OUTPUT
   ```

## 📋 工作流文件状态

### 当前可用的工作流：

1. **simple-daily-fetch.yml** (推荐)
   - ✅ 语法正确
   - ✅ 变量命名规范
   - ✅ 功能完整

2. **daily-gold-data.yml** (完整版)
   - ✅ 已修复语法错误
   - ✅ 已修复变量命名
   - ✅ 功能丰富

3. **test-fetch.yml** (测试版)
   - ✅ 仅手动触发
   - ✅ 用于测试验证

## 🧪 验证方法

### 1. 语法检查
可以使用在线YAML验证器检查语法：
- https://yaml-online-parser.appspot.com/
- https://yamlchecker.com/

### 2. 本地测试
```bash
# 使用act工具本地测试GitHub Actions
npm install -g @github/act
act workflow_dispatch
```

### 3. GitHub在线验证
- 推送到GitHub后查看Actions页面
- 语法错误会立即显示
- 可以查看详细的错误信息

## 💡 最佳实践

1. **使用简化版工作流** - 除非需要高级功能
2. **定期检查Actions运行状态** - 确保自动化正常工作
3. **使用标准的GitHub变量和Secrets** - 避免自定义保留前缀
4. **保持YAML格式整洁** - 注意缩进和空格
5. **测试后再部署** - 使用test工作流验证功能

## 🔗 相关文档

- [GitHub Actions变量文档](https://docs.github.com/en/actions/learn-github-actions/variables)
- [GitHub Actions Secrets文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [YAML语法指南](https://yaml.org/spec/1.2/spec.html)

现在您的GitHub Actions工作流已经修复完成，可以正常运行了！
