import pandas as pd


def convert_res_element(ls):
    return [
        x.strip()
        for x in ls
    ]


def extract_price_list(response):
    res = (
        response
        .xpath('//div[@data-id="priceNow"]//span')
        .re("<span>(.*).*VND</span>")
    )
    res = convert_res_element(res)
    res = [
        int(x.replace('.', ''))
        for x in res
    ]

    return res


def extract_airline_list(response):
    res = (
        response
        .xpath('//p[@class="_1L727 _3gn1_"]')
        .re("<span.*>(.*)</span>")
    )
    res = convert_res_element(res)

    return res


def extract_time_list(response):
    res = (
        response
        .xpath('//div[@class="_32ZNg"]')
        .re('title="(.+?)"')
    )

    res = convert_res_element(res)

    depart_hours = []
    arrive_hours = []
    durations = []
    for i, v in enumerate(res):
        if i % 3 == 0:
            depart_hours.append(v)
        elif i % 3 == 1:
            arrive_hours.append(v)
        elif i % 3 == 2:
            durations.append(v)

    assert len(depart_hours) == len(arrive_hours), \
        "len(depart_hours) != len(arrive_hours)"
    assert len(depart_hours) == len(durations), \
        "len(depart_hours) != len(durations)"

    return depart_hours, arrive_hours, durations


def extract_flight_info(response):
    price_list = extract_price_list(response)
    depart_hours, arrive_hours, durations = extract_time_list(response)
    airline_list = extract_airline_list(response)
    records = list(zip(
        airline_list,
        depart_hours,
        arrive_hours,
        durations,
        price_list
    ))
    assert len(price_list) == len(arrive_hours), \
        "len(price_list) != len(arrive_hours)"
    if '#depart' in str(response):
        import pdb; pdb.set_trace()
    res_df = (
        pd.DataFrame(
            records,
            columns=[
                'airline', 
                'depart_time',
                'arrive_time',
                'duration',
                'price'])
    )

    return res_df
