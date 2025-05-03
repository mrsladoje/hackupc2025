package com.pumpaj.evropo.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import java.time.LocalDateTime;

@Document(collection = "news_articles_informer")
@CompoundIndex(def = "{'url': 1, 'title': 1}", unique = true)
public class ModelInformer {
    @Id
    private String id;

    @Indexed(unique = true)
    private String url;

    private String title;

    private boolean visited = false;

    private LocalDateTime createdAt;

    private LocalDateTime lastUpdated;

    private String sourceWebsite = "https://informer.rs";

    // Constructors
    public ModelInformer() {
        this.createdAt = LocalDateTime.now();
        this.lastUpdated = LocalDateTime.now();
    }

    public ModelInformer(String url, String title) {
        this();
        this.url = url;
        this.title = title;
    }

    // Getters and Setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public boolean isVisited() {
        return visited;
    }

    public void setVisited(boolean visited) {
        this.visited = visited;
        this.lastUpdated = LocalDateTime.now();
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getLastUpdated() {
        return lastUpdated;
    }

    public void setLastUpdated(LocalDateTime lastUpdated) {
        this.lastUpdated = lastUpdated;
    }

    public String getSourceWebsite() {
        return sourceWebsite;
    }

    public void setSourceWebsite(String sourceWebsite) {
        this.sourceWebsite = sourceWebsite;
    }

    @Override
    public String toString() {
        return "ModelInformer{" +
                "id='" + id + '\'' +
                ", url='" + url + '\'' +
                ", title='" + title + '\'' +
                ", visited=" + visited +
                ", createdAt=" + createdAt +
                ", lastUpdated=" + lastUpdated +
                ", sourceWebsite='" + sourceWebsite + '\'' +
                '}';
    }
}