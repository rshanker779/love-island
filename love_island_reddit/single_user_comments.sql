select c.*
,max(s.episode_number) as episode_number
,string_agg(i.first_name, ',') as first_name
,string_agg(i.last_name, ',') as last_name
from comments c
left join comment_mentions m
on c.id = m.comment_id
left join islanders i
on m.islander_id = i.id
left join submissions s
on s.id = c.submission_id
group by c.id
having count(i.id)=1;
