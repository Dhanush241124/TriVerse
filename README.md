# Smart Water ATM

Next.js app for collecting payment with Razorpay and issuing one-time dispense tokens for an ESP32 water dispenser.

## Flow

1. User selects quantity and pays in Razorpay checkout.
2. Server verifies payment (`/api/verify-payment`) or receives signed webhook (`/api/webhook`).
3. Server stores payment and creates a short-lived dispense token.
4. ESP32 polls for token, runs pump/relay, then consumes token.

## Tech Stack

- Next.js 14 (App Router)
- React 18
- Razorpay Node SDK
- In-memory demo store (`lib/store.ts`)

## Local Setup

```bash
npm install
copy .env.example .env
npm run dev
```

Open: `http://localhost:3000`

## Environment Variables

Copy from `.env.example`:

```env
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxx
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
DEVICE_API_KEY=super_secret_device_key
DISPENSE_MS=5000
PAYMENT_NOTIFY_URL=https://your-hardware-controller.example.com/payment-event
PAYMENT_NOTIFY_SECRET=your_notify_shared_secret
PAYMENT_NOTIFY_TIMEOUT_MS=5000
```

- `NEXT_PUBLIC_RAZORPAY_KEY_ID`: Checkout key exposed to browser.
- `RAZORPAY_KEY_ID`: Server key id returned by `/api/create-order`.
- `RAZORPAY_KEY_SECRET`: Used to verify checkout signature.
- `RAZORPAY_WEBHOOK_SECRET`: Used to verify webhook signature.
- `DEVICE_API_KEY`: Required in `x-device-key` for ESP32 APIs.
- `DISPENSE_MS`: Duration (ms) returned to device for dispensing.
- `PAYMENT_NOTIFY_URL`: HTTPS webhook URL that receives payment/water events.
- `PAYMENT_NOTIFY_SECRET`: Optional shared secret sent as `x-notify-secret`.
- `PAYMENT_NOTIFY_TIMEOUT_MS`: Timeout for outbound notification request.

## Razorpay Webhook Setup

- URL: `https://<your-domain>/api/webhook`
- Event: `payment.captured`
- Secret: same value as `RAZORPAY_WEBHOOK_SECRET`

## API Endpoints

### `POST /api/create-order`
Creates Razorpay order.

Request body:

```json
{
  "amountPaise": 500,
  "machineId": "machine-1"
}
```

### `POST /api/verify-payment`
Verifies checkout signature and issues dispense token.

Request body:

```json
{
  "orderId": "order_xxx",
  "paymentId": "pay_xxx",
  "signature": "signature_xxx",
  "amount": 500,
  "machineId": "machine-1"
}
```

Success response now includes:

- `amountPaise`
- `waterMl`
- `paymentStatus` (`CAPTURED`)
- `waterStatus` (`START`)
- `notificationSent`

### `POST /api/webhook`
Accepts Razorpay signed webhooks and issues token for `payment.captured`.

Required header:

- `x-razorpay-signature`

### `GET /api/dispense-token?machineId=machine-1`
Device polls for token.

Required header:

- `x-device-key: <DEVICE_API_KEY>`

### `POST /api/consume-token`
Marks token as used and payment as dispensed.

Required header:

- `x-device-key: <DEVICE_API_KEY>`

Request body:

```json
{
  "token": "token_xxx",
  "machineId": "machine-1"
}
```

Also sends STOP notification with amount, water, and payment status.

## Outbound Notification Payload

Server sends `POST` to `PAYMENT_NOTIFY_URL` (HTTPS only) with JSON:

```json
{
  "eventType": "PAYMENT_CONFIRMED",
  "machineId": "machine-1",
  "paymentId": "pay_xxx",
  "orderId": "order_xxx",
  "amountPaise": 500,
  "amountInr": 5,
  "waterMl": 250,
  "paymentStatus": "CAPTURED",
  "waterStatus": "START",
  "dispenseToken": "token_xxx",
  "timestamp": "2026-03-09T10:15:30.000Z"
}
```

For consume/stop event:

- `eventType`: `DISPENSE_STOPPED`
- `waterStatus`: `STOP`
- `dispenseToken` is omitted.

## ESP32 Integration

Use `esp32/esp32-water-dispenser.ino` and configure:

- Wi-Fi SSID/password
- App base URL
- `MACHINE_ID`
- `DEVICE_API_KEY`
- Relay GPIO pin

For phone + ESP32 testing on local network, expose the app with a tunnel and update the base URL in sketch config.

## Important Notes

- Data is stored in memory only; restart clears payments/tokens.
- Replace `lib/store.ts` with persistent DB for production.
- Add hardware safeties and retry handling before deployment.
