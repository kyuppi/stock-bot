def should_buy(price_now, previous_price):
    if previous_price == 0:
        return False

    change_percent = (
        (price_now - previous_price)
        / previous_price
    ) * 100

    # 安全寄り：強すぎる動きは避ける
    if 0.5 <= change_percent <= 2.0:
        return True

    return False