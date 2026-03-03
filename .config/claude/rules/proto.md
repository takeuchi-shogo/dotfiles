---
paths:
  - "**/*.proto"
---

# Protocol Buffers Rules

## Field Numbering

- NEVER change a field number once assigned — it breaks wire compatibility
- Reserve numbers 1-15 for frequently used fields (1 byte encoding)
- Use `reserved` for removed fields to prevent accidental reuse

```protobuf
message User {
  reserved 3, 8;           // deleted field numbers
  reserved "old_name";     // deleted field names

  string id = 1;
  string email = 2;
}
```

## Enum Design

- First value MUST be `_UNSPECIFIED = 0` — it serves as the default/unknown state
- Never rely on zero value having meaning — always treat it as "not set"
- Prefix enum values with the enum name in UPPER_SNAKE_CASE

```protobuf
enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_CONFIRMED = 2;
  ORDER_STATUS_CANCELLED = 3;
}
```

## Naming Conventions

- Messages: `PascalCase` (e.g. `UserProfile`)
- Fields: `snake_case` (e.g. `created_at`, `user_id`)
- Enums: `PascalCase` for type, `UPPER_SNAKE_CASE` for values
- RPC methods: `PascalCase` verbs (e.g. `GetUser`, `ListOrders`)
- Files: `snake_case.proto` matching the primary message

## Package Naming

- Use domain-based package names: `package mycompany.service.v1;`
- Always include a version suffix (`v1`, `v2`) for API stability
- One package per directory — do not mix packages in the same folder

## Backward Compatibility

- NEVER remove or rename fields — deprecate with `[deprecated = true]`
- Add new fields with new numbers — existing clients ignore unknown fields
- Changing field types is a breaking change (e.g. `int32` to `string`)
- Use `oneof` for mutually exclusive fields instead of optional booleans
