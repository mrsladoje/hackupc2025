package com.pumpaj.evropo.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.CompoundIndex;

@Document(collection = "protests")
@CompoundIndex(name = "organizer_location_date_idx", def = "{'organizer': 1, 'location': 1, 'date': 1}", unique = true)
public class Protest {
    @Id
    private String id;
    private String organizer;
    private String location;
    private String date;
    private Count count;
    private Double x;
    private Double y;

    public static class Count {
        private Integer government;
        private Integer independent;

        // Getters and setters
        public Integer getGovernment() {
            return government;
        }

        public void setGovernment(Integer government) {
            this.government = government;
        }

        public Integer getIndependent() {
            return independent;
        }

        public void setIndependent(Integer independent) {
            this.independent = independent;
        }
    }

    // Getters and setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getOrganizer() {
        return organizer;
    }

    public void setOrganizer(String organizer) {
        this.organizer = organizer;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public Count getCount() {
        return count;
    }

    public void setCount(Count count) {
        this.count = count;
    }

    public Double getX() {
        return x;
    }

    public void setX(Double x) {
        this.x = x;
    }

    public Double getY() {
        return y;
    }

    public void setY(Double y) {
        this.y = y;
    }
}