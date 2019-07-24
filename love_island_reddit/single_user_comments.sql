select * from comments where id in
(
select c.id
from comments c
left join comment_mentions m
on c.id = m.comment_id
left join islanders i
on m.islander_id = i.id
group by c.id
having count(i.id)=1);