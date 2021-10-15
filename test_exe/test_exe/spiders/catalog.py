import scrapy
#import json
import time
from urllib.parse import urljoin
from collections import namedtuple


class CatalogSpider(scrapy.Spider):
  name = 'catalog'
  allowed_domains = ['magnitcosmetic.ru']
  start_urls = ['https://magnitcosmetic.ru/catalog/kosmetika/makiyazh_glaz/']


  def parse(self, response, **kwargs):
    page_count = int(response.css('option[selected="selected"]::text').re('\d+')[0])//96 + 1
    for page in range(1, page_count):
      url = f'https://magnitcosmetic.ru/catalog/kosmetika/makiyazh_glaz/?perpage=96&PAGEN_1={page}'
      yield scrapy.Request(url,  callback=self.parse_pages)

  def parse_pages(self, response, **kwargs):
    for ur in response.css('a.product__link::attr(href)').getall():
      yield scrapy.Request(url = urljoin('https://magnitcosmetic.ru', ur), cookies = {'FAVORITE_SHOP':	"136335",'geo_city_id':	"55568"}, callback = self.parse_card)


  def parse_card(self, response, **kwargs):
    for p in response.css('span.header__info_shop-title::text').getall():
      item = {
        'timestamp': time.time()
        ,'RPC': response.xpath('normalize-space(//div[contains(@class, "action-card__text note") and contains(text(), "Штрихкод")])').get()
        ,'url': response.url
        ,'brand': response.xpath('//tr/td[contains(@class, "action-card__cell") and contains(text(), "Бренд:")]/following-sibling::td/text()').get()
        ,'title': [{
          'Название':response.css('h1.action-card__name').get(),
          'Цвет': response.css('h1.action-card__name').re('(?<=цвет\s)[а-яА-я]+'),
          'Количество':response.css('h1.action-card__name').re('[а-яА-Я0-9]+?(?=\sшт)'),
          'Вес': response.css('h1.action-card__name').re('(?<=г\s)[а-яА-я]+')}]
        , 'section': [x.strip() for x in response.xpath('//a[@class = "breadcrumbs__link"]//text()').getall()[2:]],
         'stock': response.xpath('normalize-space(//div[@class="action-card__text price-none js-item_price-none"]//text())').get()
        ,'assets': {'main_image': response.css('img.product__image::attr(src)').get()}
        ,'__description': response.xpath('//div[@class = "action-card__text"]//text()').get()      
        }
      yield item





