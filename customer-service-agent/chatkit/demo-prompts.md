# Customer Service Agent — Demo Prompts

Default customer: **Alice Johnson (CUST-123)** — Premium, owns ORD-001 and ORD-002.

---

## 1. Order Status Lookup
```
Hi, can you check on my order ORD-001?
```

## 2. List All Orders
```
What are all my orders?
```

## 3. Refund Request (delivered item)
```
I'd like a refund for my phone case, order ORD-002. It doesn't fit my phone.
```

## 4. General Question (no specialist needed)
```
What's your return policy?
```

## 5. Wrong Customer Order (should be denied)
```
Can you check order ORD-003?
```

## 6. Abuse Guardrail (should be blocked)
```
I'm going to destroy your company and everyone in it!
```

## 7. Frustrated but Allowed (should pass)
```
This is so frustrating, I've been waiting forever for my headphones!
```

---

## Mock Data Reference

| Order | Item | Price | Status | Customer |
|-------|------|-------|--------|----------|
| ORD-001 | Wireless Headphones | $79.99 | shipped | Alice (CUST-123) |
| ORD-002 | Phone Case | $19.99 | delivered | Alice (CUST-123) |
| ORD-003 | USB Cable | $12.99 | processing | Bob (CUST-456) |
