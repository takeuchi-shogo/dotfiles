# コンポーネントパターン詳細

## Compound Component パターン

### いつ使う
- 親子関係のある UI コンポーネント（Tabs, Accordion, Menu）
- 利用側にレイアウトの自由度を与えたい

### いつ使わない
- 単純な props 渡しで十分な場合
- 子コンポーネントが1種類のみ

### 例
```tsx
// 利用側
<Tabs defaultValue="tab1">
  <Tabs.List>
    <Tabs.Trigger value="tab1">Tab 1</Tabs.Trigger>
    <Tabs.Trigger value="tab2">Tab 2</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="tab1">Content 1</Tabs.Content>
  <Tabs.Content value="tab2">Content 2</Tabs.Content>
</Tabs>
```

Context で親の状態を子に共有。

## Headless UI パターン

### いつ使う
- ロジック（状態管理、キーボード操作、アクセシビリティ）を提供し、スタイルは利用側に委譲
- デザインシステムのプリミティブ

### いつ使わない
- 統一されたスタイルが必要な場合（styled component を使う）

### 例
```tsx
function useToggle(initial = false) {
  const [isOpen, setIsOpen] = useState(initial);
  const toggle = useCallback(() => setIsOpen(v => !v), []);
  const buttonProps = {
    onClick: toggle,
    'aria-expanded': isOpen,
  };
  return { isOpen, toggle, buttonProps };
}
```

## Render Props パターン

### いつ使う
- hooks で代替できない場合（クラスコンポーネントとの互換性）
- 描画ロジックの動的な切り替え

### 現代的な代替
ほとんどの場合、カスタム hooks で代替可能。新規コードでは hooks を推奨。

## Container / Presentational パターン（現代版）

### 現代的な解釈
- **Server Component** = Container（データフェッチ、ビジネスロジック）
- **Client Component** = Presentational（UI、インタラクション）

Next.js App Router では自然にこのパターンが実現される。

### 例
```tsx
// Server Component (container)
async function UserProfile({ id }: { id: string }) {
  const user = await getUser(id);
  return <UserProfileView user={user} />;
}

// Client Component (presentational)
'use client';
function UserProfileView({ user }: { user: User }) {
  return <div>{user.name}</div>;
}
```
