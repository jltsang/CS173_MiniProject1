import smartpy as sp

class Lottery(sp.Contract):
    def __init__(self, admin_address):
        self.init(
            players = sp.map(l={}, tkey=sp.TNat, tvalue=sp.TAddress),
            ticket_cost = sp.tez(1),
            tickets_available = sp.nat(5),
            max_tickets = sp.nat(5),
            operator = admin_address,
        )
    
    @sp.entry_point
    def buy_ticket(self, entries):

        sp.set_type(entries, sp.TNat)
        
        # Sanity checks
        sp.verify(self.data.tickets_available > 0, "NO TICKETS AVAILABLE")
        sp.verify(self.data.tickets_available >= entries, "NOT ENOUGH TICKETS AVAILABLE")

        total = sp.utils.nat_to_mutez(entries * sp.utils.mutez_to_nat(self.data.ticket_cost))
        sp.verify(sp.amount >= total, "INVALID AMOUNT")
        
        # Storage updates
        sp.for x in sp.range(0, entries):
            self.data.players[sp.len(self.data.players)] = sp.sender
            self.data.tickets_available = sp.as_nat(self.data.tickets_available - 1)

        # Return extra tez balance to the sender
        extra_balance = sp.amount - total
        sp.if extra_balance > sp.mutez(0):
            sp.send(sp.sender, extra_balance)

    @sp.entry_point
    def end_game(self, random_number):
        sp.set_type(random_number, sp.TNat)

        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == 0, "GAME IS YET TO END")

        # Pick a winner
        winner_id = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_id]

        # Send the reward to the winner
        sp.send(winner_address, sp.balance)

        # Reset the game
        self.data.players = {}
        self.data.tickets_available = self.data.max_tickets
        
    @sp.entry_point
    def change_cost(self, cost):
        sp.set_type(cost, sp.TNat)

        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "GAME IS YET TO END")

        self.data.ticket_cost = sp.utils.nat_to_mutez(cost)

    @sp.entry_point
    def change_max(self, max):
        sp.set_type(max, sp.TNat)

        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "GAME IS YET TO END")

        self.data.max_tickets = max
        self.data.tickets_available = max

    @sp.entry_point
    def default(self):
        sp.failwith("NOT ALLOWED")

@sp.add_test(name = "main")
def test():
    scenario = sp.test_scenario()

    # Test accounts
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    mike = sp.test_account("mike")
    charles = sp.test_account("charles")
    john = sp.test_account("john")

    # Contract instance
    lottery = Lottery(admin.address)
    scenario += lottery

    # buy_ticket
    # scenario.h2("buy_ticket (valid test)")
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(1), sender = alice)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(2), sender = bob)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(3), sender = john)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(5), sender = charles)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(1), sender = mike)

    # scenario.h2("buy_ticket (failure test)")
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(1), sender = alice, valid = False)

    # scenario.h2("change max tickets")  
    # scenario += lottery.change_max(2).run(sender = admin)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(1), sender = alice)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(2), sender = bob)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(3), sender = john, valid = False)

    # scenario.h2("change ticket cost")  
    # scenario += lottery.change_cost(2000000).run(sender = admin)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(1), sender = alice, valid = False)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(2), sender = alice)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(2), sender = bob)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(3), sender = john)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(5), sender = charles)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(2), sender = mike)

    # scenario.h2("buy multiple tickets")  
    # scenario += lottery.buy_ticket(4).run(amount = sp.tez(4), sender = john)
    # scenario += lottery.buy_ticket(2).run(amount = sp.tez(2), sender = alice, valid = False)
    # scenario += lottery.buy_ticket(1).run(amount = sp.tez(1), sender = alice)
    
    # end_game
    scenario.h2("end_game (valid test)")
    scenario += lottery.end_game(21).run(sender = admin)