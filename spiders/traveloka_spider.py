import scrapy
import scrapy_splash
import pandas as pd
import os

from ..utils import extract as extract_utils
from ..utils import file as file_utils


# lua_script_wait_page = """
# function main(splash)
#   splash:set_user_agent(splash.args.ua)
#   assert(splash:go(splash.args.url))

#   -- requires Splash 2.3  
#   -- while not splash:select('.my-element') do
#   while splash:evaljs('!document.querySelector(".my-element")') do
#     splash:wait(5)
#   end
#   return {html=splash:html()}
# end
# """

# lua_script_wait_page = """
# function main(splash, args)
# assert (splash:go(args.url))
# assert (splash:wait(5))
# return {
#     html = splash: html(),
#     png = splash:png(),
#     har = splash:har(),
# }
# end
# """


class TravelokaSpider(scrapy.Spider):
    name = 'traveloka'
    o_path = './output/result.csv'

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    def start_requests(self):
        urls = [
            # 'https://www.traveloka.com/vi-vn/flight/fulltwosearch?ap=HAN.PQC&dt=12-05-2019.15-05-2019&ps=1.0.0&sc=ECONOMY'
            'https://www.traveloka.com/vi-vn/flight/fulltwosearch?ap=HAN.PQC&dt=12-05-2019.15-05-2019&ps=1.0.0&sc=ECONOMY#depart',
            'https://www.traveloka.com/vi-vn/flight/fulltwosearch?ap=HAN.PQC&dt=12-05-2019.15-05-2019&ps=1.0.0&sc=ECONOMY#return'
        ]

        for url in urls:
            if url.endswith('#depart') or url.endswith('ECONOMY'):
                yield scrapy_splash.SplashRequest(url, self.parse_depart,
                    args={
                        # optional; parameters passed to Splash HTTP API
                        'wait': 1,
                        # 'lua_source': lua_script_wait_page
                        # 'url' is prefilled from request url
                        # 'http_method' is set to 'POST' for POST requests
                        # 'body' is set to request body for POST requests
                    },
                    # dont_filter=True
                    # endpoint='render.json', # optional; default is render.html
                    # splash_url='<url>',     # optional; overrides SPLASH_URL
                    # slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                )
            elif url.endswith('#return'):
                yield scrapy_splash.SplashRequest(url, self.parse_return,
                    args={
                        # optional; parameters passed to Splash HTTP API
                        'wait': 1,
                        # 'lua_source': lua_script_wait_page
                        # 'url' is prefilled from request url
                        # 'http_method' is set to 'POST' for POST requests
                        # 'body' is set to request body for POST requests
                    },
                    # dont_filter=True
                    # endpoint='render.json', # optional; default is render.html
                    # splash_url='<url>',     # optional; overrides SPLASH_URL
                    # slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                )


    def parse_depart(self, response):
        res_df = (
            extract_utils.extract_flight_info(response)
            .assign(
                direction='depart',
                import_time=pd.Timestamp.now())
        )

        filter_df = pd.concat(
            [
                res_df
                    .loc[
                        lambda df:
                            df['price'] == df['price'].min()]
                    .assign(crawl_type='cheapest'),
                res_df
                    .loc[
                        lambda df:
                            (df['airline'] == 'Jetstar')
                            &
                            (df['depart_time'] == '09:45')]
                    .assign(crawl_type='family')
            ],
            axis=0
        )

        file_utils.save_or_append(filter_df, path=self.o_path)
        if filter_df.shape[0] > 0:
            self.log(f"Saved depart output!")
        else:
            self.log(f"depart filter_df has no records!")

    
    def parse_return(self, response):
        res_df = (
            extract_utils.extract_flight_info(response)
            .assign(
                direction='return',
                import_time=pd.Timestamp.now())
        )

        filter_df = pd.concat(
            [
                res_df
                    .loc[
                        lambda df:
                            df['price'] == df['price'].min()]
                    .assign(crawl_type='cheapest'),
                res_df
                    .loc[
                        lambda df:
                            (df['airline'] == 'Jetstar')
                            &
                            (df['depart_time'] == '12:30')]
                    .assign(crawl_type='family')
            ],
            axis=0
        )

        file_utils.save_or_append(filter_df, path=self.o_path)
        if filter_df.shape[0] > 0:
            self.log(f"Saved return output!")
        else:
            self.log(f"return filter_df has no records!")
