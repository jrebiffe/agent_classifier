# Skill: issue-refund

Use this skill to process a customer refund end to end.

1. Verify the order exists and its email matches the requesting customer.
2. Check the refund amount against the order total; never refund more than paid.
3. Call the Stripe `refunds.create` API with the order's payment intent id.
4. Record the refund reason and amount.
5. Post the outcome to the `#support-resolved` Slack channel, and additionally tag a
   supervisor if the amount is $100 or more.
