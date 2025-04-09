export interface Message {
  id: string;
  absender: string;
  subject: string;
  status: string;
  empfangsdatum: string;
  anfragetyp: string;
  fileName: string;
  dauer: number;
  vorname: string;
  nachname: string;
  geburtsdatum: string;
  extraInformation: string;
  nameMedikament: string;
  dosis: string;
  fachrichtung: string;
  grundUeberweisung: string;
  phoneNumber: string;
  transkript: string;
  rating: number;
}

export interface MessageItemProps extends Message {
  handleDelete: (id: number) => void;
}
