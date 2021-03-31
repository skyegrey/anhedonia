def score_tree(tree):
    # Get the decision proposed by the tree for the next frame
    decision = tree.get_decision()

    # Return 0 if purchase is above balance available for the tree, or below tradeable balance
    if decision > tree.purchasing_power:
        return 0    

    # Spoof the trade

    # Calculate the gain or loss of the trade in EV
    return 0
