package com.pumpaj.evropo.repository;

import com.pumpaj.evropo.model.Protest;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ProtestRepository extends MongoRepository<Protest, String> {
    Optional<Protest> findByOrganizerAndLocationAndDate(String organizer, String location, String date);
}