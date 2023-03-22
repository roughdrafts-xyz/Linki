# MetadataRepository
#   add_group(refId, group)
#   add_title(refId, title)
#   get_groups(refId)
#   get_title(refId)
# ArticleRepository = (ContentRepository + MetadataRepository + HistoryRepository)
#   update_article(prefId, bytes)

# SKIP Until Optimize
# FS/DiffRepository
#   add_diff(refId, prefId, refBytes, prefBytes)
#   get_diff(refId, prefId)

# Done

# ContentRepository
#   add_content(bytes)
#   get_content(refId)

# HistoryRepository
#   add_edit(prefId, refId)
#   get_parent(refId)
#   get_children(refId)
