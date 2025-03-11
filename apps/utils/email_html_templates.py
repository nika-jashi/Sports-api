def email_verify(otp):
    html_body = f"""
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: 'Arial', sans-serif;
      background-color: #f4f4f4;
      text-align: center;
      padding: 20px;
    }}

    .container {{
      max-width: 400px;
      margin: 0 auto;
      background-color: #ffffff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      border-top: 2px solid #007bff;
      border-bottom: 2px solid #007bff;
      overflow: hidden;
    }}

    h1, p, .otp, .highlight {{
      text-align: center;
    }}

    h1 {{
      color: #333333;
    }}

    p {{
      color: #666666;
      margin-bottom: 20px;
    }}

    .otp {{
      font-size: 24px;
      font-weight: bold;
      color: #007bff;
    }}

    .highlight {{
      font-weight: bold;
      color: #007bff;
    }}
  </style>
</head>

<body>
  <div class="container">
    <h1>Your Account Verification</h1>
    <p>Your One-Time Code Is</p>
    <p class="otp">{otp}</p>
    <p>This Code Is Valid For <span class="highlight">One Hour</span></p>
  </div>
</body>
</html>

    """
    return html_body


def password_reset(otp):
    html_body = f"""
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: 'Arial', sans-serif;
      background-color: #f4f4f4;
      text-align: center;
      padding: 20px;
    }}

    .container {{
      max-width: 400px;
      margin: 0 auto;
      background-color: #ffffff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      border-top: 2px solid #007bff;
      border-bottom: 2px solid #007bff;
      overflow: hidden;
    }}

    h1, p, .otp, .highlight {{
      text-align: center;
    }}

    h1 {{
      color: #333333;
    }}

    p {{
      color: #666666;
      margin-bottom: 20px;
    }}

    .otp {{
      font-size: 24px;
      font-weight: bold;
      color: #007bff;
    }}

    .highlight {{
      font-weight: bold;
      color: #007bff;
    }}
  </style>
</head>

<body>
  <div class="container">
    <h1>Password Reset For Account</h1>
    <p>Your One-Time Code Is</p>
    <p class="otp">{otp}</p>
    <p>This Code Is Valid For <span class="highlight">Ten Minutes</span></p>
  </div>
</body>
</html>

    """
    return html_body
