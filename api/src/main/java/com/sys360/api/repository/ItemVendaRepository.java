package com.sys360.api.repository;

import com.sys360.api.modelo.ItemVenda;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface ItemVendaRepository extends JpaRepository<ItemVenda, UUID> {
}
