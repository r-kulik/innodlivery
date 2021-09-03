'''
statuses:
0 - in main menu
1 - waiting for input order entity
2 - waiting for input order reward
'''

database_file = 'data.db'

main_menu = 0
input_order_status = 1
input_order_reward_status = 2



greeting = """Hello! I`m InnoDelivery.
I can help you to find people who will deliver something to you from Kazan.
Also I will help you to find a chance to get some reward for delivery.
"""
order_button = 'Order something from Kazan'
picking_button = 'Pick an order'
my_orders_button = 'My orders'

many_tickets_error_text = "You have already created five orders. Please, delete some of your previous orders to create new ones. To delete, go to \"My orders\""

order_question = "What do you need to get from Kazan?"
reward_question = "Great! And what is a reward for deliverman?"
ticket_created_message = "Your order is now in order list"

ticket_format = """
Order #{}.
Deliver: {}
Reward: {}
Contact: @{}
"""
delete_text = "Delete this order"
no_orders_text = "You have not any orders yet. Create new!"